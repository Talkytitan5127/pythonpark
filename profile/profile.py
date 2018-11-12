#!/usr/bin/python3

import time
from types import FunctionType
from functools import wraps

#decorator
def profile(obj, class_name=None):
    if not isinstance(obj, FunctionType):
        for key, value in obj.__dict__.items():
            if isinstance(value, FunctionType):
                func = getattr(obj, key)
                setattr(obj, key, profile(func, class_name=obj.__name__))
        return obj
    @wraps(obj)
    def process(*args, **kwargs):
        begin = time.time()
        name = obj.__name__
        if class_name is not None:
            name = "{}.{}".format(class_name, name)
        print("`{}` started".format(name))
        result = obj(*args, **kwargs)
        print("`{}` finished in {:.6f}".format(name, time.time() - begin))
        return result
    return process