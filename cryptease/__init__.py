import os
import io
import struct
import pickle
import logging
import tempfile as tf
import collections as col
import cryptease.compat as compat
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

logger = logging.getLogger(__file__)

Key = col.namedtuple('Key', ['key', 'metadata'])
Random = col.namedtuple('Random', ['source'])
PBKDF2 = col.namedtuple('PBKDF2', ['alg', 'rounds', 'salt'])
AES = col.namedtuple('AES', ['bits', 'mode'])
Integer = col.namedtuple('Integer', ['letter', 'size'])
Int = Integer(letter='I', size=struct.calcsize('I'))

def kdf(passphrase, salt=None):
    '''
    Generate an encryption key using PBKDF2 key derivation 
    with 100,000 rounds of SHA-256
    
    Example::
        >>> import base64
        >>> from cryptease import kdf
        >>> key = kdf('password')
        >>> base64.b64encode(key.key)
        't0BfCC5i1WqvucYsrL4H8/YlGOakMJimZLrQ5sXUzgY='
        >>> key = kdf('password', key.metadata)
        >>> base64.b64encode(key.key)
        't0BfCC5i1WqvucYsrL4H8/YlGOakMJimZLrQ5sXUzgY='
    
    :param passphrase: Passphrase
    :type passphrase: str
    :param salt: Encryption salt
    :type salt: str
    :returns: Encryption key
    :rtype: :mod:`cryptease.Key`
    '''
    length = 32
    rounds = 100000
    if not salt:
        salt = os.urandom(length)
    if isinstance(salt, compat.basestring):
        salt = compat.bytes(salt, encoding='latin-1')
    backend = default_backend()
    kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=length,
            salt=salt,
            iterations=rounds,
            backend=backend)
    key = kdf.derive(compat.bytes(passphrase, encoding='utf8'))
    return Key(key=key, metadata=PBKDF2(alg='sha256', rounds=rounds, salt=salt))

def key_from_file(raw, passphrase):
    '''
    Generate encryption key from encrypted file and passphrase

    :param raw: Raw encrypted content
    :type raw: a .read()-supporting file-like object
    :param passphrase: Passphrase
    :type passphrase: str
    :returns: Encryption key
    :rtype: :mod:`cryptease.Key`
    '''
    header,_ = read_header(raw)
    return kdf(passphrase, salt=header['kdf'].salt)

def randkey():
    '''
    Generate a random encryption key
    
    Example::
        >>> from cryptease import randkey
        >>> key = randkey()
    
    :returns: Encryption key
    :rtype: :mod:`cryptease.Key`
    '''
    key = os.urandom(32)
    return Key(key=key, metadata=Random(source='urandom'))

def encrypt(raw, key, chunk_size=1e8, filename=None):
    '''
    Encrypt content using AES Cipher Feedback (CFB 8-bit shift register)
    and return as a stream of bytes or save to a file

    :param raw: Raw content
    :type raw: a .read()-supporting file-like object
    :param key: Encryption key
    :type key: :mod:`cryptease.Key`
    :param chunk_size: Chunk size in bytes
    :type chunk_size: int
    '''
    if not filename:
        return encrypt_to_stream(raw, key, chunk_size)
    return encrypt_to_file(filename, raw, key, chunk_size)
        
def encrypt_to_stream(raw, key, chunk_size=1e8):
    '''
    Encrypt content using AES Cipher Feedback (CFB 8-bit shift register)
    and return as a stream of bytes

    :param raw: Raw content
    :type raw: a .read()-supporting file-like object
    :param key: Encryption key
    :type key: :mod:`cryptease.Key`
    :param chunk_size: Chunk size in bytes
    :type chunk_size: int
    '''
    chunk_size = int(chunk_size)
    # generate unique initialization vector
    iv = os.urandom(16)
    # generate header content
    header = __header(AES(bits=256, mode='CFB8'), key.metadata, iv)
    while True:
        chunk = header.read(chunk_size)
        if not chunk:
            break
        yield chunk
    # generate initialization vector
    bio = io.BytesIO(iv)
    while True:
        chunk = bio.read(chunk_size)
        if not chunk:
            break
        yield chunk
    # generate payload content
    cipher = Cipher(algorithms.AES(key.key), modes.CFB8(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()
    while True:
        chunk = raw.read(chunk_size)
        if not chunk:
            break
        yield encryptor.update(chunk)
    yield encryptor.finalize()

def __header(ciphermeta, kdfmeta, iv):
    '''
    Helper function to create encryption header
    '''
    bio = io.BytesIO()
    header = {
        'cipher' : ciphermeta,
        'kdf' : kdfmeta,
        'iv' : iv
    }
    bin_header = pickle.dumps(header)
    bin_header_len = struct.pack(Int.letter, len(bin_header))
    bio.write(bin_header_len)
    bio.write(bin_header)
    bio.seek(0)
    return bio

def encrypt_to_file(filename, raw, key, chunk_size=1e8):
    '''
    Encrypt content using AES Cipher Feedback (CFB 8-bit shift register)
    and safely save to a file
    
    :param filename: Path to save file
    :type filename: str
    :param raw: Raw content
    :type raw: a .read()-supporting file-like object
    :param key: Encryption key
    :type key: :mod:`cryptease.Key`
    '''
    filename = os.path.expanduser(filename)
    dirname = os.path.dirname(filename)
    with tf.NamedTemporaryFile(dir=dirname, prefix='.cryptease', suffix='.tmp',
                               delete=False) as tmp:
        for chunk in encrypt(raw, key, chunk_size):
            tmp.write(chunk)
    os.rename(tmp.name, filename)

def decrypt(raw, key, chunk_size=1e8, filename=None):
    '''
    Decrypt content using AES Cipher Feedback (CFB 8-bit shift register)
    and return as a stream of bytes or save to a file

    :param raw: Raw encrypted content
    :type raw: a .read()-supporting file-like object
    :param key: Encryption key
    :type key: :mod:`cryptease.Key`
    :param chunk_size: Chunk size in bytes
    :type chunk_size: int
    :param filename: Path to save file
    :type filename: str
    '''
    if not filename:
        return decrypt_to_stream(raw, key, chunk_size)
    return decrypt_to_file(filename, raw, key, chunk_size)
    
def decrypt_to_stream(raw, key, chunk_size=1e8):
    '''
    Decrypt content using AES Cipher Feedback (CFB 8-bit shift register)
    and return as a stream of bytes

    :param raw: Raw encrypted content
    :type raw: a .read()-supporting file-like object
    :param key: Encryption key
    :type key: :mod:`cryptease.Key`
    :param chunk_size: Chunk size in bytes
    :type chunk_size: int
    '''
    chunk_size = int(chunk_size)
    header,payload_start = read_header(raw)
    raw.seek(payload_start)
    iv = raw.read(16)
    cipher = Cipher(algorithms.AES(key.key), modes.CFB8(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()
    while True:
        chunk = raw.read(chunk_size)
        if not chunk:
            break
        yield decryptor.update(chunk)
    yield decryptor.finalize()

def decrypt_to_file(filename, raw, key, chunk_size=1e8):
    '''
    Decrypt content using AES Cipher Feedback (CFB 8-bit shift register)
    and save to a file

    :param filename: Path to save file
    :type filename: str
    :param raw: Raw encrypted content
    :type raw: a .read()-supporting file-like object
    :param key: Encryption key
    :type key: :mod:`cryptease.Key`
    :param chunk_size: Chunk size in bytes
    :type chunk_size: int
    '''
    filename = os.path.expanduser(filename)
    dirname = os.path.dirname(filename)
    with tf.NamedTemporaryFile(dir=dirname, prefix='.decrypt', suffix='.tmp',
                               delete=False) as tmp:
        for chunk in decrypt(raw, key, chunk_size):
            tmp.write(chunk)
    os.rename(tmp.name, filename)

def read_header(raw):
    '''
    Read header from encrypted file

    :param raw: Raw encrypted content
    :type raw: a .read()-supporting file-like object
    :returns: Tuple of (header, payload byte position)
    :rtype: tuple
    '''
    _length = raw.read(Int.size)
    length = struct.unpack(Int.letter, _length)[0]
    _header = raw.read(length)
    header = compat.pickle.loads(_header)
    raw.seek(0)
    return header,length + Int.size

def buffer(iterable, buffer_size=io.DEFAULT_BUFFER_SIZE):
    class IterStream(io.RawIOBase):
        def __init__(self):
            self.leftover = None
        def readable(self):
            return True
        def readinto(self, b):
            try:
                l = len(b)  
                chunk = self.leftover or next(iterable)
                output, self.leftover = chunk[:l], chunk[l:]
                b[:len(output)] = output
                return len(output)
            except StopIteration:
                return 0
    return io.BufferedReader(IterStream(), buffer_size=buffer_size)

