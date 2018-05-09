import sys
import pickle

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

def loads(s, encoding='latin-1'):
    if PY3:
        return pickle.loads(s, encoding=encoding)
    else:
        return pickle.loads(s)

