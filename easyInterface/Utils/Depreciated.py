#   Licensed under the GNU General Public License v3.0
#   Copyright (c) of the author (github.com/wardsimon)
#   Created: 26/2/2020

__author__ = 'github.com/wardsimon'
__version__ = '0.0.1'

import functools
import warnings

from typing import Callable

warnings.simplefilter('always', DeprecationWarning)


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


def deprecated_function(new_function_name=None):
    new_name = new_function_name

    def inner(func):
        @functools.wraps(func)
        def function_wrapper(*args, **kwargs):
            if new_name is not None:
                warnings.warn('{} is deprecated; use {}'.format(func.__module__ + '.' + func.__name__, new_name),
                              DeprecationWarning, stacklevel=2)

            else:
                warnings.warn('{} is deprecated'.format(func.__module__ + '.' + func.__name__), DeprecationWarning,
                              stacklevel=2)
            return func(*args, **kwargs)

        return function_wrapper

    return inner


def depreciated_class(new_class_name=None):
    """
    A decorator to tell you that the class is depreciated
    """

    def class_wrapper(klass):
        old_init = klass.__init__

        def new_init(self, *args, **kwargs):
            if new_name is not None:
                warnings.warn('{} is deprecated; use {}'.format(klass.__module__ + '.' + klass.__name__, new_name),
                              DeprecationWarning, stacklevel=2)

            else:
                warnings.warn('{} is deprecated'.format(klass.__module__ + '.' + klass.__name__), DeprecationWarning,
                              stacklevel=2)
            old_init(self, *args, **kwargs)

        klass.__init__ = new_init
        return klass

    new_name = None
    if isinstance(new_class_name, Callable):
        return class_wrapper(new_class_name)
    else:
        new_name = new_class_name
    return class_wrapper
