import sys
from . import pickle

PY2 = sys.version_info[0] == 2 
PY3 = sys.version_info[0] == 3 

if PY3: 
    basestring = str
else:
    basestring = basestring

__bytes = bytes
def bytes(s, encoding='ascii'):
    if PY3:
        return __bytes(s, encoding=encoding)
    return __bytes(s)

