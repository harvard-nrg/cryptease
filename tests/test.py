#!/usr/bin/env python

import os
import io
import filecmp
import unittest
import tempfile as tf
import encrypt as enc

DIR = os.path.dirname(__file__)

def test_string():
    encrypted = b''
    decrypted = b''
    key = enc.randkey()
    original = b'Hello, World!'
    for chunk in enc.encrypt(io.BytesIO(original), key):
        encrypted += chunk
    for chunk in enc.decrypt(io.BytesIO(encrypted), key):
        decrypted += chunk  
    assert decrypted == original
    
def test_file():
    key = enc.randkey()
    encrypted = b''
    decrypted = b''
    with open(os.path.join(DIR, 'file.bin'), 'rb') as fo:
        original = fo.read()
    with open(os.path.join(DIR, 'file.bin'), 'rb') as fo:
        for chunk in enc.encrypt(fo, key):
            encrypted += chunk
    for chunk in enc.decrypt(io.BytesIO(encrypted), key):
        decrypted += chunk
    assert decrypted == original

def test_write_file():
    original = b'''Lorem ipsum dolor sit amet, consectetur adipiscing elit,
                sed do eiusmod tempor incididunt ut labore et dolore 
                magna aliqua. Ut enim ad minim veniam, quis nostrud 
                exercitation ullamco laboris nisi ut aliquip ex ea commodo 
                consequat.'''
    passphrase = 'foo bar biz bat'
    key = enc.kdf(passphrase)
    with tf.NamedTemporaryFile(dir=DIR, prefix='enc', delete=False) as enc_tmp:
        enc.encrypt_to_file(enc_tmp.name, io.BytesIO(original), key)
    key = None
    with tf.NamedTemporaryFile(dir=DIR, prefix='dec', delete=False) as dec_tmp:
        with open(enc_tmp.name, 'rb') as fo:
            key = enc.key_from_file(fo, passphrase)
            enc.decrypt_to_file(dec_tmp.name, fo, key)
    os.remove(enc_tmp.name)
    with open(dec_tmp.name, 'rb') as fo:
        decrypted = fo.read()
    os.remove(dec_tmp.name)
    assert decrypted == original

