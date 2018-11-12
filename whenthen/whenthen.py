#!/usr/bin/python3

import pdb
from functools import wraps

class whenthen:
    def __init__(self, function):
        self.main = function
        self._when = []
        self._then = []
        self._pos = 0

    def when(self, function):
        if len(self._then) != len(self._when):
            raise KeyError
        self._when.append(function)
        return self

    def then(self, function):
        if self._pos >= len(self._when):
            raise KeyError
        self._then.append(function)
        self._pos += 1
        return self

    def __call__(self, elem):
        if len(self._when) != len(self._then):
            raise ValueError
        for ind in range(self._pos):
            if self._when[ind](elem):
                return self._then[ind](elem)
        return self.main(elem)
