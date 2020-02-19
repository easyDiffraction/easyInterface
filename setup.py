import os
from setuptools import setup, find_packages
import json

try:
    with open(os.path.join('easyInterface', 'Release.json')) as json_file:
        project_info = json.load(json_file)
except FileNotFoundError:
    project_info = dict()

setup(
    name=project_info.get('name', 'easyInterface'),
    version=project_info.get('version', '0.0.0'),
    packages=find_packages(),
    package_data={'': ['Release.json']},
    data_files={'examples': ['examples/*']},
    include_package_data=True,
    url=project_info.get('url', 'https://github.com/easyDiffraction/easyInterface'),
    license='GPL3',
    author=project_info.get('author', 'Simon Ward'),
    author_email='',
    description='Description  easyInterface - The easy way to interface with crystallographic calculators ',
    install_requires=[
        'cryspy>=0.2.0',
        'dictdiffer',
        'asteval'
    ],
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
