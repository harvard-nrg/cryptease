#!/usr/bin/env python

import os
import io
import filecmp
import unittest
import tempfile as tf
import cryptease as crypt 

DIR = os.path.dirname(__file__)

def test_string():
    encrypted = b''
    decrypted = b''
    key = crypt.randkey()
    original = b'Hello, World!'
    for chunk in crypt.encrypt(io.BytesIO(original), key):
        encrypted += chunk
    for chunk in crypt.decrypt(io.BytesIO(encrypted), key):
        decrypted += chunk  
    assert decrypted == original
    
def test_file():
    key = crypt.randkey()
    encrypted = b''
    decrypted = b''
    with open(os.path.join(DIR, 'file.bin'), 'rb') as fo:
        original = fo.read()
    with open(os.path.join(DIR, 'file.bin'), 'rb') as fo:
        for chunk in crypt.encrypt(fo, key):
            encrypted += chunk
    for chunk in crypt.decrypt(io.BytesIO(encrypted), key):
        decrypted += chunk
    assert decrypted == original

def test_write_file():
    original = b'''Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                sed do eiusmod tempor incididunt ut labore et dolore 
                magna aliqua. Ut enim ad minim veniam, quis nostrud 
                exercitation ullamco laboris nisi ut aliquip ex ea commodo 
                consequat.'''
    passphrase = 'foo bar biz bat'
    key = crypt.kdf(passphrase)
    with tf.NamedTemporaryFile(dir=DIR, prefix='enc', delete=False) as enc_tmp:
        crypt.encrypt_to_file(enc_tmp.name, io.BytesIO(original), key)
    key = None
    with tf.NamedTemporaryFile(dir=DIR, prefix='dec', delete=False) as dec_tmp:
        with open(enc_tmp.name, 'rb') as fo:
            key = crypt.key_from_file(fo, passphrase)
            crypt.decrypt_to_file(dec_tmp.name, fo, key)
    os.remove(enc_tmp.name)
    with open(dec_tmp.name, 'rb') as fo:
        decrypted = fo.read()
    os.remove(dec_tmp.name)
    assert decrypted == original

