Cryptease: easier encryption
============================
[![Build Status](https://travis-ci.org/harvard-nrg/cryptease.svg?branch=master)](https://travis-ci.org/harvard-nrg/cryptease)

cryptease provides an simple API and command line tool for encrypting and decrypting
files and other blobs of data. cryptease is able to encrypt and decrypt content in 
chunks, which can be useful for encrypting and decrypting extremely large files. It 
also supports opening encrypted files as a file-like-object for reading decrypted 
content on the fly.

## Table of contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Basic command line usage](#basic-command-line-usage)
4. [Basic API usage](#basic-api-usage)
5. [Advanced](#advanced)
6. [Comments](#comments)

## Requirements
Cryptease works with Python versions 2 and 3.

## Installation
The easiest way to install `cryptease` is with `pip`

```bash
pip install cryptease
```

## Basic command line usage
There is a simple command line utility shipped with this library that can be 
used to quickly encrypt a file

```bash
$ crypt.py --encrypt file.txt --output-file file.enc
```

and decrypt a file

```bash
$ crypt.py --decrypt file.enc --output-file file.dec
```

## Basic API usage
The `cryptease` library provides an way to build custom software and applications
that need to encrypt or decrypt files in one shot or one chunk at a time. Use 
`cryptease.encrypt` to encrypt a string in memory using AES-256 encryption

```python
import io
import cryptease as crypt

content = 'Hello, World!'

key = crypt.kdf('password')

ciphertext = b''
for chunk in crypt.encrypt(content, key):
    ciphertext += chunk

for chunk in crypt.decrypt(io.BytesIO(ciphertext), key):
    print chunk,
```

To serialize the encrpyted data (i.e., cipher text) and some metadata about the 
key to a flat file, simply pass the `filename` argument

```python
import io
import cryptease as crypt

content = 'Hello, World!'

key = crypt.kdf('password')
crypt.encrypt(io.BytesIO(content), key, filename='file.enc')
```

To deserialize the encrypted file to a decrypted file, simply `open` the file,
pass it to `cryptease.encrypt`, and pass the `filename` parameter to 
`cryptease.decrypt`

```python
import cryptease as crypt

with open('file.enc') as fp:
    key = crypt.key_from_file(fp, 'password')
    crypt.decrypt(fp, key, filename='file.dec')
```

