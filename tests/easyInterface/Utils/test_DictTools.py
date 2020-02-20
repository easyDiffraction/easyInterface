import pytest
from easyInterface.Utils.DictTools import PathDict, UndoableDict


def test_PathDict():
    d = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
    assert d == {'a': 1, 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}

    d1 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
    d2 = PathDict(dict(a=1, b=2, c=dict(d=333, e=dict(f=4, g=555))))
    assert d1.dictComparison(d2) == ([['c', 'd'], ['c', 'e', 'g']], [333, 555])

    d1 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
    d2 = "string"
    with pytest.raises(TypeError):
        d1.dictComparison(d2)


def test_non_nested_dict():
    d = UndoableDict()

    # Add item

    assert d == {}
    assert d.undoText() == ""
    assert d.redoText() == ""

    d['a'] = 'AAA'
    assert d == {'a': 'AAA'}
    assert d.undoText() == "Adding: a = AAA"
    assert d.redoText() == ""

    d['b'] = 'BBB'
    assert d == {'a': 'AAA', 'b': 'BBB'}
    assert d.undoText() == "Adding: b = BBB"
    assert d.redoText() == ""

    d['c'] = 'CCC'
    assert d == {'a': 'AAA', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Adding: c = CCC"
    assert d.redoText() == ""

    d.undo()
    assert d == {'a': 'AAA', 'b': 'BBB'}
    assert d.undoText() == "Adding: b = BBB"
    assert d.redoText() == "Adding: c = CCC"

    d.redo()
    assert d == {'a': 'AAA', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Adding: c = CCC"
    assert d.redoText() == ""

    # Set item

    d['a'] = '---'
    assert d == {'a': '---', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Setting: a = ---"
    assert d.redoText() == ""

    d['b'] = '+++'
    assert d == {'a': '---', 'b': '+++', 'c': 'CCC'}
    assert d.undoText() == "Setting: b = +++"
    assert d.redoText() == ""

    d.undo()
    assert d == {'a': '---', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Setting: a = ---"
    assert d.redoText() == "Setting: b = +++"

    d.undo()
    assert d == {'a': 'AAA', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Adding: c = CCC"
    assert d.redoText() == "Setting: a = ---"

    d.undo()
    assert d == {'a': 'AAA', 'b': 'BBB'}
    assert d.undoText() == "Adding: b = BBB"
    assert d.redoText() == "Adding: c = CCC"

    d.redo()
    assert d == {'a': 'AAA', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Adding: c = CCC"
    assert d.redoText() == "Setting: a = ---"

    d.redo()
    assert d == {'a': '---', 'b': 'BBB', 'c': 'CCC'}
    assert d.undoText() == "Setting: a = ---"
    assert d.redoText() == "Setting: b = +++"

    # Add item again

    d['e'] = 999
    assert d == {'a': '---', 'b': 'BBB', 'c': 'CCC', 'e': 999}
    assert d.undoText() == "Adding: e = 999"
    assert d.redoText() == ""


def test_nested_dict():
    # Add item

    d = UndoableDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
    d.clearUndoStack()
    assert d.undoText() == ""
    assert d.redoText() == ""

    d['a'] = "---"
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: a = ---"
    assert d.redoText() == ""

    d.undo()
    assert d == {'a': 1, 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == ""
    assert d.redoText() == "Setting: a = ---"

    d.redo()
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: a = ---"
    assert d.redoText() == ""

    d.setItemByPath(['c', 'e', 'g'], '***')
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': '***'}}}
    assert d.undoText() == "Setting: ['c', 'e', 'g'] = ***"
    assert d.redoText() == ""

    d.undo()
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: a = ---"
    assert d.redoText() == "Setting: ['c', 'e', 'g'] = ***"

    d.redo()
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': '***'}}}
    assert d.undoText() == "Setting: ['c', 'e', 'g'] = ***"
    assert d.redoText() == ""


def test_bulk_update():
    # Add item

    d = UndoableDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
    d.clearUndoStack()
    assert d.undoText() == ""
    assert d.redoText() == ""

    d['b'] = 999
    assert d == {'a': 1, 'b': 999, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: b = 999"
    assert d.redoText() == ""

    d['b'] = 2
    assert d == {'a': 1, 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: b = 2"
    assert d.redoText() == ""

    d['b'] = 777
    assert d == {'a': 1, 'b': 777, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: b = 777"
    assert d.redoText() == ""

    d.undo()
    assert d == {'a': 1, 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: b = 2"
    assert d.redoText() == "Setting: b = 777"

    assert d.canUndo() is True
    assert d.canRedo() is True

    d.startBulkUpdate("Bulk update")

    assert d.canUndo() is False
    assert d.canRedo() is False

    d['a'] = "---"
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == ""
    assert d.redoText() == ""

    d.setItemByPath(['c', 'e', 'g'], '***')
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': '***'}}}
    assert d.undoText() == ""
    assert d.redoText() == ""

    d.endBulkUpdate()

    d.undo()
    assert d == {'a': 1, 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': 5}}}
    assert d.undoText() == "Setting: b = 2"
    assert d.redoText() == "Bulk update"

    d.redo()
    assert d == {'a': '---', 'b': 2, 'c': {'d': 3, 'e': {'f': 4, 'g': '***'}}}
    assert d.undoText() == "Bulk update"
    assert d.redoText() == ""

# d1 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
#   d2 = PathDict(dict(a=1, b=2, c=dict(d=333, e=dict(f=4, g=555))))
#   print("A", d1.dictComparison(d2))
# 
#   d1 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
#   d2 = {'a': 1, 'b': 2, 'c': {'d': 333, 'e': {'f': 4, 'g': 555}}}
#   print("c", d1.dictComparison(d2))
# 
#   d1 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
#   d2 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4))))
#   print("D", d1.dictComparison(d2))
# 
#   d1 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(g=5))))
#   d2 = PathDict(dict(a=1, b=2, c=dict(d=3, e=dict(f=4, g=5))))
#   print("E", d1.dictComparison(d2))
# 
#   d1 = PathDict({'a': 1, 'b': 2, 'c': PathDict({'d': 3, 'e': PathDict({'f': 4})})})
#   d2 = PathDict({'a': 1, 'b': 2, 'c': PathDict({'d': 3, 'e': PathDict({'f': 4, 'g': 5})})})
#   print("F", d1.dictComparison(d2))
# 
#   d1 = PathDict({'a': 1, 'b': 2})
#   d2 = PathDict({'a': 1, 'b': 2, 'c': PathDict({'d': 3, 'e': PathDict({'f': 4, 'g': 5})})})
#   print("G", d1.dictComparison(d2))
# 
#   d1 = PathDict({'a': 1, 'b': 2, 'm': 0})
#   d2 = PathDict({'a': 9, 'c': PathDict({'d': 3, 'e': PathDict({'f': 4, 'g': 5})}), 'm': 1})
#   print("H", d1.dictComparison(d2))
# 
#   d1 = PathDict({'a': 9, 'c': {'d': 3, 'e 1': {'f': 4, 'g': 5}}, 'm': 1, 'o': {'p': {'q': 8, 'r.2': 0}}})
#   d2 = {'a': 99, 'c': {'d': 3, 'e 1': {'f': 4, 'g': 55, 'h': 66}}, 'm': 11, 'o': {'p': {'r.2': 2}}}
#   print("K", d1.dictComparison(d2))
# 
#   d1 = PathDict({'a': 9, 'c': PathDict({'d': 3, 'e 1': PathDict({'f': 4, 'g': 5})}), 'm': 1,
#                  'o': PathDict({'p': PathDict({'q': 8, 'r.2': 0})})})
#   d2 = PathDict({'a': 99, 'c': PathDict({'d': 3, 'e 1': PathDict({'f': 4, 'g': 55, 'h': 66})}), 'm': 11,
#                  'o': PathDict({'p': PathDict({'r.2': 2})})})
#   print("M", d1.dictComparison(d2))
# 
#   d1 = PathDict({'a': 9, 'c': PathDict({'d': 3, 'e 1': PathDict({'f': 4, 'g': 5})}), 'm': 1,
#                  'o': PathDict({'p': PathDict({'q': 8, 'r.2': 0})})})
#   d2 = PathDict(
#       {'aa': PathDict(alpha=1, beta=2), 'a': 99, 'c': PathDict({'d': 3, 'e 1': PathDict({'f': 4, 'g': 55, 'h': 66})}),
#        'm': 11, 'o': PathDict({'p': PathDict({'r.2': 2})})})
#   print("N", d1.dictComparison(d2))
#   k, v = d1.dictComparison(d2)
#   for item in v:
#       print(item, type(item))
# 
#   d1 = PathDict(a=[1, 2, 3], b={'c': 2})
#   d2 = PathDict(a=[1, 2, 3, 4], b={'c': 2, 'd': 4, 3: 5})
#   print("O", d1.dictComparison(d2))
#   print(list(dictdiffer.diff(d1, d2)))
#   # k, v = d1.dictComparison(d2)
#   d2 = UndoableDict({'a': 9, 'c': PathDict({'d': 3, 'e': PathDict({'f': 4, 'g': 5})}), 'm': 1})
#   print(d2)
#   d2.rmItemByPath(['c', 'e', 'g'])
#   print(d2)
#   d2.undo()
#   print(d2)
#   d2.redo()
#   print(d2)
