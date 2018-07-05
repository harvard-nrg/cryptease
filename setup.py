from setuptools import setup, find_packages

setup(name='encrypt',
      description='encrypt',
      author='Neuroinformatics Research Group',
      author_email='support@neuroinfo.org',
      url='http://neuroinformatics.harvard.edu/',
      packages=find_packages(),
      scripts=[
        'scripts/crypt.py',
        'scripts/keyring.py'
      ]
)

