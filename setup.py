from setuptools import setup

setup(
    name='EasyInterface',
    version='0.0.2',
    packages=['EasyInterface', 'EasyInterface.Utils', 'EasyInterface.Calculators', 'EasyInterface.DataClasses',
              'EasyInterface.DataClasses.Utils', 'EasyInterface.DataClasses.DataObj',
              'EasyInterface.DataClasses.PhaseObj'],
    url='http://www.easydiffraction.org',
    license='GPL3',
    author='Simon Ward',
    author_email='',
    description='Description  EasyInterface - The easy way to interface with crystallographic calculators ',
    install_requires=[
        'cryspy>=0.2.0',
        'dictdiffer',
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
