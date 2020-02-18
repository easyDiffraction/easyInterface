import os
from setuptools import setup
from easyInterface.Utils.Helpers import getReleaseInfo

project_info = getReleaseInfo(os.path.join('easyInterface', 'Release.yml'))['release']

setup(
    name=project_info['name'],
    version=project_info['version'],
    packages=['easyInterface', 'easyInterface.Utils', 'easyInterface.Diffraction',
              'easyInterface.Diffraction.Calculators', 'easyInterface.Diffraction.DataClasses',
              'easyInterface.Diffraction.DataClasses.Utils', 'easyInterface.Diffraction.DataClasses.DataObj',
              'easyInterface.Diffraction.DataClasses.PhaseObj'],
    package_data={'': ['Release.yml']},
    include_package_data=True,
    url=project_info['url'],
    license='GPL3',
    author=project_info['author'],
    author_email='',
    description='Description  easyInterface - The easy way to interface with crystallographic calculators ',
    install_requires=[
        'cryspy>=0.2.0',
        'dictdiffer',
        'asteval',
        'pyyaml'
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
