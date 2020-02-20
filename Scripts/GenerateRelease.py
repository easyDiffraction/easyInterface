import BasicFunctions
import sys
import os
import json


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


if __name__ == '__main__':

    file_name = sys.argv[1]
    BasicFunctions.printTitle('Writing changelog - {}'.format(file_name))
    createReleaseNotes(os.path.join('easyInterface', 'Release.json'), file_name)

