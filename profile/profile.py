#!/usr/bin/python3

import time
from types import FunctionType
from functools import wraps

#decorator
def profile(obj):
    if not isinstance(obj, FunctionType):
        for key, value in obj.__dict__.items():
            if isinstance(value, FunctionType):
                func = getattr(obj, key)
                setattr(obj, key, profile(func))
        return obj
    @wraps(obj)
    def process(*args, **kwargs):
        begin = time.time()
        name = obj.__name__
        print("`{}` started".format(name))
        result = obj(*args, **kwargs)
        print("`{}` finished in {:.6f}".format(name, time.time() - begin))
        return result
    return process