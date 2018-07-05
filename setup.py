from setuptools import setup, find_packages

requires = [
    'cryptography',
    'paramiko'
]

setup(name='encrypt',
      description='encrypt',
      author='Neuroinformatics Research Group',
      author_email='support@neuroinfo.org',
      url='http://neuroinformatics.harvard.edu/',
      packages=find_packages(),
      install_requires=requires,
      scripts=[
        'scripts/crypt.py',
        'scripts/keyring.py'
      ]
)

