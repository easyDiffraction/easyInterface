__author__ = 'simonward'
__version__ = "2020_02_01"

from collections import deque, UserDict
from copy import deepcopy
from typing import Union, Any, NoReturn, Tuple, List
import abc

import dictdiffer


class UndoStack:
    """
    Implement a version of QUndoStack without the QT
    """

    def __init__(self, max_history: Union[int, type(None)] = None):
        self._history = deque(maxlen=max_history)
        self._future = deque(maxlen=max_history)
        self._macro_running = False
        self._macro = dict(text="", commands=[])
        self._max_history = max_history

    @property
    def history(self) -> deque:
        return self._history

    def push(self, command) -> NoReturn:
        """
        Add a command to the history stack
        """
        if self._macro_running:
            self._macro['commands'].append(command)
        else:
            self._history.appendleft(command)
        command.redo()
        self._future = deque(maxlen=self._max_history)

    def clear(self) -> NoReturn:
        """
        Remove any commands on the stack and reset the state
        """
        self._history = deque(maxlen=self._max_history)
        self._future = deque(maxlen=self._max_history)
        self._macro_running = False
        self._macro = dict(text="", commands=[])

    def undo(self) -> NoReturn:
        """
        Undo the last change to the stack
        """
        if self.canUndo():
            command = self._history[0]
            self._future.appendleft(command)
            self._history.popleft()
            if isinstance(command, dict):
                for item in command['commands'][::-1]:
                    item.undo()
            else:
                command.undo()

    def redo(self) -> NoReturn:
        """
        Redo the last `undo` command on the stack
        """
        if len(self._future) > 0:
            command = self._future[0]
            if not self._macro_running:
                self._history.appendleft(command)
            self._future.popleft()
            if isinstance(command, dict):
                for item in command['commands']:
                    item.redo()
            else:
                command.redo()

    def beginMacro(self, text: str) -> NoReturn:
        """
        Start a bulk update i.e. multiple commands under one undo/redo command
        """
        if self._macro_running:
            raise AssertionError
        self._macro_running = True
        self._macro = dict(text=text, commands=[])

    def endMacro(self) -> NoReturn:
        """
        End a bulk update i.e. multiple commands under one undo/redo command
        """
        if not self._macro_running:
            raise AssertionError
        self._macro_running = False
        self._history.appendleft(self._macro)

    def canUndo(self) -> bool:
        """
        Can the last command be undone?
        """
        return len(self._history) > 0 and not self._macro_running

    def canRedo(self) -> bool:
        """
        Can we redo a command?
        """
        return len(self._future) > 0 and not self._macro_running

    def redoText(self) -> str:
        """
        Text associated with a redo item.
        """
        if self.canRedo():
            if isinstance(self._future[0], dict):
                return self._future[0]['text']
            else:
                return self._future[0]._text
        else:
            return ''

    def undoText(self) -> str:
        """
        Text associated with a undo item.
        """
        if self.canUndo():
            if isinstance(self._history[0], dict):
                return self._history[0]['text']
            else:
                return self._history[0]._text
        else:
            return ''


class UndoCommand(metaclass=abc.ABCMeta):
    """
    The Command interface pattern
    """

    def __init__(self, obj) -> None:
        self._obj = obj
        self._text = None

    @abc.abstractmethod
    def undo(self) -> NoReturn:
        """
        Undo implementation which should be overwritten
        """
        pass

    @abc.abstractmethod
    def redo(self) -> NoReturn:
        """
        Redo implementation which should be overwritten
        """
        pass

    def setText(self, text: str) -> NoReturn:
        self._text = text


class _EmptyCommand(UndoCommand):
    """
    The _EmptyCommand class is the custom base class of all undoable commands
    stored on a UndoStack.
    """

    def __init__(self, dictionary: 'UndoableDict', key: Union[str, list], value: Any):
        super().__init__(self)
        self._dictionary = dictionary
        self._key = key
        self._new_value = value
        self._old_value = dictionary.getItem(key)


class _AddItemCommand(_EmptyCommand):
    """
    The _AddItemCommand class implements a command to add a key-value pair to
    the UndoableDict-base_dict dictionary.
    """

    def __init__(self, dictionary: 'UndoableDict', key: Union[str, list], value: Any):
        super().__init__(dictionary, key, value)
        self.setText("Adding: {} = {}".format(self._key, self._new_value))

    def undo(self) -> NoReturn:
        self._dictionary._realDelItem(self._key)

    def redo(self) -> NoReturn:
        self._dictionary._realAddItem(self._key, self._new_value)


class _SetItemCommand(_EmptyCommand):
    """
    The _SetItemCommand class implements a command to modify the value of
    the existing key in the UndoableDict-base_dict dictionary.
    """

    def __init__(self, dictionary: 'UndoableDict', key: Union[str, list], value: Any):
        super().__init__(dictionary, key, value)
        self.setText("Setting: {} = {}".format(self._key, self._new_value))

    def undo(self) -> NoReturn:
        if self._new_value is not self._old_value:
            if self._old_value is None:
                self._dictionary._realDelItem(self._key)
            else:
                self._dictionary._realSetItem(self._key, self._old_value)

    def redo(self) -> NoReturn:
        if self._new_value is not self._old_value:
            self._dictionary._realSetItem(self._key, self._new_value)


class _RemoveItemCommand(_EmptyCommand):
    """
    The _SetItemCommand class implements a command to modify the value of
    the existing key in the UndoableDict-base_dict dictionary.
    """

    def __init__(self, dictionary: 'UndoableDict', key: Union[str, list]):
        super().__init__(dictionary, key, None)
        self.setText("Removing: {}".format(self._key))

    def undo(self) -> NoReturn:
        self._dictionary._realAddItemByPath(self._key, self._old_value)

    def redo(self) -> NoReturn:
        self._dictionary._realDelItem(self._key)


class PathDict(UserDict):
    """
    The PathDict class extends a python dictionary with methods to access its nested
    elements by list-base_dict path of keys.
    """

    # Private methods

    def _realSetItem(self, key: Union[str, List], value: Any) -> NoReturn:
        """Actually changes the value for the existing key in dictionary."""
        if isinstance(key, list):
            self.getItemByPath(key[:-1])[key[-1]] = value
        else:
            super().__setitem__(key, value)

    def _realAddItem(self, key: str, value: Any) -> NoReturn:
        """Actually adds a key-value pair to dictionary."""
        super().__setitem__(key, value)

    def _realDelItem(self, key: Union[str, list]) -> NoReturn:
        """Actually deletes a key-value pair from dictionary."""
        try:
            if isinstance(key, list):
                del self.getItemByPath(key[:-1])[key[-1]]
            else:
                super().__delitem__(key)
                # del self[key]
        except TypeError as ex:
            raise KeyError(str(ex))

    def _realSetItemByPath(self, keys: list, value: Any) -> NoReturn:
        """Actually sets the value in a nested object by the key sequence."""
        self.getItemByPath(keys[:-1])[keys[-1]] = value

    def _realAddItemByPath(self, keys: list, value: Any) -> NoReturn:
        """Actually sets the value in a nested object by the key sequence."""
        item = self.getItemByPath(keys[:-1])
        if isinstance(item, dictdiffer.LIST_TYPES):
            item.insert(keys[-1], value)
        else:
            item[keys[-1]] = value

    # Public methods

    def __setitem__(self, key: str, val: Any) -> NoReturn:
        """Overrides default dictionary assignment to self[key] implementation."""
        if key in self:
            self._realSetItem(key, val)
        else:
            self._realAddItem(key, val)

    def setItemByPath(self, keys: list, value: Any) -> NoReturn:
        """Set a value in a nested object by key sequence."""
        self._realSetItem(keys, value)

    def setItem(self, key: Union[str, list], value: Any) -> NoReturn:
        """Set a value in a nested object by key sequence or by simple key."""
        if isinstance(key, list):
            self.setItemByPath(key, value)
        else:
            self[key] = value

    def getItemByPath(self, keys: list, default=None) -> Any:
        """Returns a value in a nested object by key sequence."""
        item = self
        for key in keys:
            if isinstance(item, list):
                item = item[key]
            else:
                if key in item.keys():
                    item = item[key]
                else:
                    return default
        return item

    def rmItemByPath(self, keys: list) -> NoReturn:
        self._realDelItem(keys)

    def getItem(self, key: Union[str, list], default=None) -> Any:
        """Returns a value in a nested object. Key can be either a sequence
        or a simple string."""
        if isinstance(key, list):
            return self.getItemByPath(key, default)
        else:
            return self.get(key, default)

    def asDict(self) -> dict:
        """Returns self as a python dictionary."""
        base_dict = deepcopy(self.data)
        for key in base_dict.keys():
            item = base_dict[key]
            if hasattr(item, 'asDict'):
                base_dict[key] = item.asDict()
        return base_dict

    def dictComparison(self, another_dict: Union['PathDict', dict], ignore=None) -> Tuple[list, list, list]:
        """
        Compare self to a dictionary or PathDict and return the update path and value
        :param ignore: What to ignore e.g. set(['a']))
        :param another_dict: dict or PathDict to compare self to
        :return: path and value updates for self to become newDict
        """

        if not isinstance(another_dict, (PathDict, dict)):
            raise TypeError

        type_list = []
        key_list = []
        value_list = []

        items = list(dictdiffer.diff(self, another_dict, ignore=ignore, tolerance=1E-8))

        for item in items:
            type = item[0]
            node = item[1]
            changes = item[2]
            if type == dictdiffer.CHANGE:
                dest = dictdiffer.utils.dot_lookup(self, node, parent=True)
                if isinstance(node, dictdiffer.string_types):
                    path = node.split('.')
                    last_node = path[-1]
                    path = path[:-1]
                else:
                    path = node[:-1]
                    last_node = node[-1]
                if isinstance(dest, dictdiffer.LIST_TYPES):
                    last_node = int(last_node)
                path.append(last_node)
                _, new_value = changes
                modifier = self.setItemByPath
                key_list.append(path)
                value_list.append(new_value)
                type_list.append(modifier)
            elif type == dictdiffer.ADD:
                for key, value in changes:
                    dest = dictdiffer.utils.dot_lookup(self, node)
                    path = node.split('.')
                    if isinstance(dest, (dictdiffer.LIST_TYPES, dictdiffer.SET_TYPES)):
                        if isinstance(dest, dictdiffer.LIST_TYPES):
                            dest = deepcopy(dest)
                            dest.insert(key, value)
                        else:
                            dest = value
                        new_value = dest
                        modifier = self.setItemByPath
                    else:
                        path.append(key)
                        new_value = value
                        modifier = self.setItemByPath
                    key_list.append(path)
                    value_list.append(new_value)
                    type_list.append(modifier)

            elif type == dictdiffer.REMOVE:
                for key, value in changes:
                    dest = dictdiffer.utils.dot_lookup(self, node)
                    path = node.split('.')
                    if isinstance(dest, dictdiffer.SET_TYPES):
                        new_value = ()
                        modifier = self.setItemByPath
                    else:
                        if path[-1] == '':
                            path = path[:-1]
                        path.append(key)
                        new_value = ()
                        modifier = self.rmItemByPath
                    key_list.append(path)
                    value_list.append(new_value)
                    type_list.append(modifier)

        return key_list, value_list, type_list


class UndoableDict(PathDict):
    """
    The UndoableDict class implements a PathDict-base_dict class with undo/redo
    functionality base_dict on QUndoStack.
    """

    def __init__(self, *args, **kwargs):
        self.__stack = UndoStack()
        super().__init__(*args, **kwargs)

    # Public methods: dictionary-related

    def __setitem__(self, key: str, val: Any) -> NoReturn:
        """
        Calls the undoable command to override PathDict assignment to self[key]
        implementation and pushes this command on the stack.
        """
        if key in self:
            self.__stack.push(_SetItemCommand(self, key, val))
        else:
            self.__stack.push(_AddItemCommand(self, key, val))

    def __delitem__(self, key):
        self.__stack.push(_RemoveItemCommand(self, key))

    @property
    def macro_running(self) -> bool:
        return self.__stack._macro_running

    def setItemByPath(self, keys: list, value: Any) -> NoReturn:
        """
        Calls the undoable command to set a value in a nested object
        by key sequence and pushes this command on the stack.
        """
        # For backwards compatibility
        if isinstance(value, tuple):
            if len(value) == 0:
                self.__stack.push(_RemoveItemCommand(self, keys))
        else:
            self.__stack.push(_SetItemCommand(self, keys, value))

    def rmItemByPath(self, keys: list) -> NoReturn:
        self.__stack.push(_RemoveItemCommand(self, keys))

    # Public methods: undo/redo-related

    def clearUndoStack(self) -> NoReturn:
        """
        Clears the command stack by deleting all commands on it, and
        returns the stack to the clean state.
        """
        self.__stack.clear()

    def canUndo(self) -> bool:
        """
        :return true if there is a command available for undo;
        otherwise returns false.
        """
        return self.__stack.canUndo()

    def canRedo(self) -> bool:
        """
        :return true if there is a command available for redo;
        otherwise returns false.
        """
        return self.__stack.canRedo()

    def undo(self) -> NoReturn:
        """
        Undoes the current command on stack.
        """
        self.__stack.undo()

    def redo(self) -> NoReturn:
        """
        Redoes the current command on stack.
        """
        self.__stack.redo()

    def undoText(self) -> str:
        """
        :return the current command on stack.
        """
        return self.__stack.undoText()

    def redoText(self) -> str:
        """
        :return the current command on stack.
        """
        return self.__stack.redoText()

    def startBulkUpdate(self, text='Bulk update') -> NoReturn:
        """
        Begins composition of a macro command with the given text description.
        """
        if self.macro_running:
            print('Macro already running')
            return
        self.__stack.beginMacro(text)

    def endBulkUpdate(self) -> NoReturn:
        """
        Ends composition of a macro command.
        """
        if not self.macro_running:
            print('Macro not running')
            return
        self.__stack.endMacro()

    def bulkUpdate(self, key_list: list, item_list: list, text='Bulk update') -> NoReturn:
        """
        Performs a bulk update base_dict on a list of keys and a list of values
        :param key_list: list of keys or path keys to be updated
        :param item_list: the value to be updated
        :return: None
        """
        if text != 'Bulk update':
            self.startBulkUpdate(text)
        for key, value in zip(key_list, item_list):
            self.setItemByPath(key, value)
        if text != 'Bulk update':
            self.endBulkUpdate()
