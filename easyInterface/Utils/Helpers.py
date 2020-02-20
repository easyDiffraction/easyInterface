import os
import json
import operator
import webbrowser
from functools import reduce
from time import time
from functools import wraps

from easyInterface import logger


def nested_get(dictionary: dict, keys_list: list):
    """Access a nested object in root by key sequence."""
    try:
        return reduce(operator.getitem, keys_list, dictionary)
    except:
        return ""


def nested_set(dictionary: dict, keys_list: list, value):
    """Get a value in a nested object in root by key sequence."""
    nested_get(dictionary, keys_list[:-1])[keys_list[-1]] = value


def find_in_obj(obj: dict, condition, path=None):
    """Find the path to an dict object"""
    if path is None:
        path = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            new_path = list(path)
            new_path.append(key)
            for result in find_in_obj(value, condition, path=new_path):
                yield result
            if condition == key:
                new_path = list(path)
                new_path.append(key)
                yield new_path


def open_url(url=""):
    """
    Open the given URL in the default system browser
    """
    try:
        webbrowser.open('file://' + os.path.realpath(url))
    except Exception as ex:
        logger.logger.info("Report viewing failed: " + str(ex))


def get_num_refine_pars(project_dict):
    # Get number of parameters
    numPars = 0
    for path in find_in_obj(project_dict, 'refine'):
        keys_list = path[:-1]
        hide = nested_get(project_dict, keys_list + ['hide'])
        if hide:
            continue
        if nested_get(project_dict, keys_list + ['refine']):
            numPars = numPars + 1
    return numPars


def getExamplesDir():
    return os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'examples')


def getReleaseInfo(file_path):
    try:
        with open(file_path) as json_file:
            project_info = json.load(json_file)
    except FileNotFoundError:
        project_info = {
            "name": "easyInterface",
            "version": "0.0.0",
            "date": "01 Jan 2020",
            "author": "Simon Ward",
            "url": "https://github.com/easyDiffraction/easyInterface",
            "comments": '',
            "changes": []
        }
    return project_info


def createReleaseNotes(release_file_path, save_file='CHANGELOG.txt'):
    release_info = getReleaseInfo(release_file_path)
    release_body = '# {} - v{}\n'.format(release_info['name'], release_info['version'])
    release_body += '\n'
    release_body += '{}\n'.format(release_info['comments'])
    release_body += '\n'
    for feature in release_info['changes']:
        release_body += '* {}\n'.format(feature)
    with open(save_file, 'w') as file_writer:
        file_writer.write(release_body)



# Useful decorators
def counted(func):
    """
    Counts how many times a function has been called and adds a `func.calls` to it's properties
    :param func: Function to be counted
    :return: Results from function call
    """

    def wrapped(*args, **kwargs):
        wrapped.calls += 1
        return func(*args, **kwargs)

    wrapped.calls = 0
    return wrapped


def time_it(func):
    """
    Times a function and reports the time either to the class' log or the base logger
    :param func: function to be timed
    :return: callable function with timer
    """
    name = func.__module__ + '.' + func.__name__
    time_logger = logger.getLogger('timer.' + name)

    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            time_logger.debug(f"\033[1;34;49mExecution time: {end_ if end_ > 0 else 0} ms\033[0m")

    return _time_it
