from setuptools import setup

setup(
    name='easyInterface',
    version='0.0.4',
    packages=['easyInterface', 'easyInterface.Utils', 'easyInterface.Diffraction',
              'easyInterface.Diffraction.Calculators', 'easyInterface.Diffraction.DataClasses',
              'easyInterface.Diffraction.DataClasses.Utils', 'easyInterface.Diffraction.DataClasses.DataObj',
              'easyInterface.Diffraction.DataClasses.PhaseObj'],
    package_data={'': ['Release.yml']},
    include_package_data=True,
    url='http://www.easydiffraction.org',
    license='GPL3',
    author='Simon Ward',
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
