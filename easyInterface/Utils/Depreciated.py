#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 26/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import functools
import warnings


def deprecated_alias(**aliases):
    def deco(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            rename_kwargs(f.__name__, kwargs, aliases)
            return f(*args, **kwargs)

        return wrapper

    return deco


def rename_kwargs(func_name, kwargs, aliases):
    for alias, new in aliases.items():
        if alias in kwargs:
            if new in kwargs:
                raise TypeError('{} received both {} and {}'.format(
                    func_name, alias, new))
            warnings.warn('{} is deprecated; use {}'.format(alias, new),
                          DeprecationWarning, stacklevel=2)
            kwargs[new] = kwargs.pop(alias)


def deprecated(newName):
    new_name = newName

    def inner(func):
        @functools.wraps(func)
        def function_wrapper(*args, **kwargs):
            warnings.warn('{} is deprecated; use {}'.format(func.__module__ + func.__name__, new_name),
                          DeprecationWarning, stacklevel=2)
            return func(*args, **kwargs)
        return function_wrapper
    return inner
