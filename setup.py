import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'cryptography'
]

test_requirements = [
    'pytest'
]

about = dict()
with open(os.path.join(here, 'cryptease', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(),
    install_requires=requires,
    tests_require=test_requirements,
    scripts=[
        'scripts/crypt.py',
        'scripts/keyring.py'
    ],
    extras_require={
        'ssh': ['paramiko']
    }
)

