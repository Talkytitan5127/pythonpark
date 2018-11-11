#!/usr/bin/python3

import os

class dir_dict:
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
    

    def __len__(self):
        return len(self.keys())

    def __contains__(self, key):
        return key in self.keys()
    
    def __iter__(self):
        for name in self.keys():
            yield name
    
    def keys(self):
        return os.listdir(self.path)
    
    def values(self):
        return [self.__getitem__(key) for key in self.keys()]
    
    def items(self):
        return list(zip(self.keys(), self.values())) 

    def clear(self):
        for name in self.keys():
            os.remove(self.path+name)
        return
    
    def get(self, key, default=None):
        if key in self.keys():
            return self.__getitem__(key)
        else:
            return default
           