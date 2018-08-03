#!/usr/bin/env python
'''
File encryption/decryption utility
'''
import os
import sys
import logging
import getpass as gp
import argparse as ap
import cryptease as crypt
try:
    import paramiko
    logging.getLogger('paramiko').setLevel(logging.ERROR)
except ImportError:
    pass

# python 3 compat
try:
    input = raw_input
except NameError:
    pass
try:
    import urlparse as up
except ImportError:
    import urllib.parse as up

logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.INFO)

def main():
    parser = ap.ArgumentParser('File encryption/decryption utility')
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('--decrypt', action='store_true', 
        help='Decrypt file')
    group1.add_argument('--encrypt', action='store_true',
        help='Encrypt file')
    parser.add_argument('-o', '--output-file',
        help='Output file')
    parser.add_argument('--debug', action='store_true',
        help='Enable debug messages')
    parser.add_argument('file',
        help='File to encrypt or decrypt')
    args = parser.parse_args()

    # get file content
    raw = get(args.file)

    # get salt from file header if decrypting
    salt = None
    if args.decrypt:
        header,_ = crypt.read_header(raw)
        salt = header['kdf'].salt

    # read passphrase (ask twice for --encrypt)
    if 'ENCRYPT_PASS' in os.environ:
        passphrase = os.environ['ENCRYPT_PASS']
    else:
        passphrase = gp.getpass('enter passphrase: ')
        if args.encrypt:
            reentered = gp.getpass('re-enter passphrase: ')
            if passphrase != reentered:
                logger.critical('passphrases do not match')
                sys.exit(1)

    # get key
    key = crypt.kdf(passphrase, salt=salt)

    # lock or unlock the file
    if args.decrypt:
        if not args.output_file:
            stdout = os.fdopen(sys.stdout.fileno(), 'wb')
            for chunk in crypt.decrypt(raw, key):
                stdout.write(chunk)
        else:
            if overwrite(args.output_file):
                logger.info('saving {}'.format(args.output_file))
                crypt.decrypt(raw, key, filename=args.output_file)
    elif args.encrypt:
        if not args.output_file:
            stdout = os.fdopen(sys.stdout.fileno(), 'wb')
            for chunk in crypt.encrypt(raw, key):
                stdout.write(chunk)
        else:
            if overwrite(args.output_file):
                logger.info('saving {}'.format(args.output_file))
                crypt.encrypt(raw, key, filename=args.output_file)

def get(f):
    '''
    Get file content from URI
    '''
    uri = up.urlparse(f)
    username = uri.username
    if not username:
        username = gp.getuser()
    if uri.scheme in ['', 'file']:
        content = open(uri.path, 'rb')
    elif uri.scheme == 'ssh':
        with paramiko.SSHClient() as client:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
            client.load_system_host_keys()
            try:
                client.connect(uri.hostname, username=username, password='')
            except paramiko.ssh_exception.AuthenticationException:
                password = gp.getpass('enter password for {}@{}: '.format(username, uri.hostname))
                client.connect(uri.hostname, username=username, password=password)
            chan = client.get_transport().open_session()
            chan.exec_command("cat '{}'".format(uri.path))
            content = chan.makefile('r', 1024)
            stderr = chan.makefile_stderr('r', 1024)
            exit_status = chan.recv_exit_status()
            if exit_status != 0:
                raise SSHError(stderr.read())
    else:
        raise URIError('unexpected scheme: {}'.format(uri.scheme))
    return content

class URIError(Exception):
    pass

class SSHError(Exception):
    pass

def overwrite(f):
    '''
    Prompt user before overwriting a file
    '''
    if not os.path.exists(f):
        return True
    count = 1
    ans = None
    while ans not in ['y', 'n']:
        ans = input('overwrite existing file [y/n]: ').lower()
        count += 1
        if count > 3:
            return False
    if ans == 'y':
        return True
    return False

if __name__ == '__main__':
    main()

