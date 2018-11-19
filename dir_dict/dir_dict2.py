#!/usr/bin/python3

import os
from collections.abc import MutableMapping

class dir_dict(MutableMapping):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        if self.path[-1] != '/':
            self.path += '/'
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        
    def __setitem__(self, key, value):
        filename = self.path + key
        with open(filename, 'w') as f:
            f.write(value)
    
    def __getitem__(self, key):
        filename = self.path + key
        result = ''
        try:
            with open(filename, 'r') as f:
                for i in f:
                    result += i
            return result
        except Exception:
            raise KeyError

    def __delitem__(self, key):
        if not os.path.exists(self.path+key):
            raise KeyError
        os.remove(self.path+key)

    def __iter__(self):
        for name in os.listdir(self.path):
            yield name

    def __len__(self):
        return len(os.listdir(self.path))
