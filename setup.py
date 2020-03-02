import json
import os

from setuptools import setup, find_packages

try:
    with open(os.path.join('easyInterface', 'Release.json')) as json_file:
        project_info = json.load(json_file)
except FileNotFoundError:
    project_info = dict()

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

long_description += '\n\n## Changelog -v{}\n'.format(project_info['version'])
long_description += '\n{}'.format(project_info['comments'])
for comment in project_info['changes']:
    long_description += '\n* {}'.format(comment)

setup(
    name=project_info.get('name', 'easyInterface'),
    version=project_info.get('version', '0.0.0'),
    packages=find_packages(),
    include_package_data=True,
    url=project_info.get('url', 'https://github.com/easyDiffraction/easyInterface'),
    license='GPL3',
    author=project_info.get('author', 'Simon Ward'),
    author_email='',
    description='easyInterface - The easy way to interface with crystallographic calculators ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'cryspy>=0.2.0',
        'dictdiffer',
        'asteval',
        'numpy'
    ],
    platforms=['any'],
    tests_require=['pytest',
                   'pytest_mock'
                   ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',  # Again, pick a license
        'Programming Language :: Python :: 3.6',
    ],
)
