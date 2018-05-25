Encrypt: a general purpose encryption library
=============================================
[![Build Status](https://travis-ci.org/harvard-nrg/encrypt.svg?branch=master)](https://travis-ci.org/harvard-nrg/encrypt)

Encrypt provides a simple API and command line tool for encrypting and decrypting
files and blobs of data.

## Table of contents
1. [Requirements](#requirements)
2. [Installation](#installation)
3. [Basic command line usage](#basic-command-line-usage)
4. [Basic API usage](#basic-api-usage)
5. [Advanced](#advanced)
6. [Comments](#comments)

## Requirements
Encrypt works with Python versions 2 and 3.

## Installation
The simplest way to install `encrypt` is with the excellent `pipenv` ✨🍰✨ 
package manager

```bash
$ pip install --user pipenv
$ git clone https://github.com/harvard-nrg/encrypt.git
$ cd encrypt
$ pipenv install
  🐍   ▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉ 17/17 — 00:00:05
```

You can also install using plain old `pip`

```bash
$ pip install --user pipenv
$ git clone https://github.com/harvard-nrg/encrypt.git
$ cd encrypt
$ pipenv lock -r > requirements.txt
$ pip install -r requirements.txt
```

## Basic command line usage
There is a simple command line utility shipped with this library that can be 
used to quickly encrypt a file

```bash
$ crypt.py --encrypt file.txt --output-file file.enc
```

and to decrypt a file

```bash
$ crypt.py --decrypt file.enc --output-file file.dec
```

## Basic API usage
The `encrypt` library provides an API to build custom software and applications
that need to encrypt or decrypt files, and perhaps do so chunk by chunk.

Use `encrypt.encrypt` to encrypt content in memory using AES-256 encryption

```python
import io
import encrypt as enc

content = 'Hello, World!'

key = enc.kdf('password')

ciphertext = b''
for chunk in enc.encrypt(content, key):
    ciphertext += chunk

for chunk in enc.decrypt(io.BytesIO(ciphertext), key):
    print chunk,
```

To serialize the encrpyted data (i.e., cipher text) and key metadata to a 
flat file, simply pass the `filename` argument

```python
import io
import encrypt as enc

content = 'Hello, World!'

key = enc.kdf('password')
enc.encrypt(io.BytesIO(content), key, filename='file.enc')
```

To deserialize the encrypted file to a decrypted file, simply `open` the file,
pass it to `encrypt.encrypt`, and pass the `filename` parameter to 
`encrypt.decrypt`

```python
import encrypt as enc

with open('file.enc') as fp:
    key = enc.key_from_file(fp, 'password')
    enc.decrypt(fp, key, filename='file.dec')
```

