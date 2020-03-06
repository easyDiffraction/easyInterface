import os
import pytest
from easyInterface.Utils.Helpers import *


def test_nested_get():
    d = dict(a=1, b=dict(c=2, d=3))
    result = nested_get(d, ['b', 'c'])
    assert result == 2

    result = nested_get(d, ['a', 'e'])
    assert result == ""


def test_nested_set():
    d = dict(a=1, b=dict(c=2, d=3))
    nested_set(d, ['b', 'c'], 5)
    assert d['b']['c'] == 5


def test_find_in_obj():
    d = dict(a=1, b=dict(c=2, d=3))
    result = list(find_in_obj(d, 'c'))
    assert result == [['b', 'c']]


def test_getReleaseInfo():
    file = os.path.join('easyInterface', 'Release.json')
    info = getReleaseInfo(file)
    assert isinstance(info, dict)
    keys = info.keys()
    assert 'name' in keys
    assert 'version' in keys
    assert 'url' in keys
    assert info['name'] == 'easyInterface'

    file = os.path.join('easyInterface', 'NoRelease.yml')
    info = getReleaseInfo(file)
    assert isinstance(info, dict)
    keys = info.keys()
    assert 'name' in keys
    assert 'version' in keys
    assert 'url' in keys
    assert info['name'] == 'easyInterface'
    assert info['version'] == '0.0.0'


def test_counted():
    @counted
    def fun():
        pass

    assert fun.calls == 0
    f = fun()
    assert fun.calls == 1
    f = fun()
    assert fun.calls == 2


def test_createReleaseNotes():
    def writeRL(*args):
        createReleaseNotes('easyInterface/Release.json', *args)
        if len(args) == 0:
            file = 'CHANGELOG.txt'
        else:
            file = args[0]
        assert os.path.isfile(file)
        with open(file, 'r') as file_reader:
            file_contents = file_reader.read()
        assert '# easyInterface' in file_contents
        assert '* ' in file_contents
        os.remove(file)

    save_file = 'test.txt'
    writeRL()
    writeRL(save_file)
