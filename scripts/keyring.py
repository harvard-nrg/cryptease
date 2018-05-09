#!/usr/bin/env python
'''
Keyring query command line tool
'''
import os
import sys
import json
import logging
import getpass as gp
import encrypt as enc
import argparse as ap

logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.INFO)

def main():
    parser = ap.ArgumentParser('File encryption/decryption utility')
    parser.add_argument('--keyring', default='~/.nrg-keyring.enc',
                        type=os.path.expanduser, help='Keyring file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--phoenix-study',
                       help='Return passphrase for PHOENIX study')
    group.add_argument('--beiwe-study',
                       help='Return passphrase for Beiwe study')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug messages')
    args = parser.parse_args()

    # read encrypted keyring file
    raw = open(args.keyring)

    # get salt from raw file header
    salt = None
    header,_ = enc.read_header(raw)
    salt = header['kdf'].salt

    # read passphrase from an env or command line
    if 'NRG_KEYRING_PASS' in os.environ:
        passphrase = os.environ['NRG_KEYRING_PASS']
    else:
        passphrase = gp.getpass('enter passphrase: ')

    # construct decryption key
    key = enc.kdf(passphrase, salt=salt)

    # decrypt the keyring content
    content = ''
    for chunk in enc.decrypt(raw, key):
        content += chunk
    js = json.loads(content)

    # return what the user requested
    try:
        if args.phoenix_study:
            sys.stdout.write(js['kitchen']['SECRETS'][args.phoenix_study])
        elif args.beiwe_study:
            sys.stdout.write(js['beiwe']['SECRETS'][args.beiwe_study])
    except KeyError as e:
        logger.critical('key not found {0}'.format(e))
        sys.exit(1)

if __name__ == '__main__':
    main()

