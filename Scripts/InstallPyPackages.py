#!/usr/bin/env python3

import sys
import BasicFunctions


# FUNCTIONS

def printSysPath():
    for path in sys.path:
        if path:
            print(path)


def upgradePip():
    message = "upgrade PIP"
    try:
        BasicFunctions.run('python', '-m', 'pip', 'install', '--upgrade', 'pip')
    except Exception as exception:
        BasicFunctions.printFailMessage(message, exception)
        sys.exit()
    else:
        BasicFunctions.printSuccessMessage(message)


def installFromGit(owner, repo, branch, egg):
    url = "git://github.com/{0}/{1}.git@{2}#egg={3}".format(owner, repo, branch, egg)
    message = "install from '{}'".format(url)
    try:
        BasicFunctions.run('pip', 'install', '-e', url, exit_on_error=False)
    except Exception as exception:
        BasicFunctions.printFailMessage(message, exception)
        # sys.exit()
    else:
        BasicFunctions.printSuccessMessage(message)


def install(*packages):
    for package in packages:
        message = "install '{}'".format(package)
        try:
            BasicFunctions.run('pip', 'install', package)
        except Exception as exception:
            BasicFunctions.printFailMessage(message, exception)
            sys.exit()
        else:
            BasicFunctions.printSuccessMessage(message)


# MAIN


if __name__ == '__main__':
    BasicFunctions.printTitle('Upgrade PIP and install packages')

    upgradePip()

    #installFromGit(owner='ikibalin', repo='cryspy', branch='transition-to-version-0.2', egg='cryspy_0.2.0_beta')
    install(
        'cryspy',
        'dictdiffer',
        'asteval',
        'pytest',
        'pytest_mock',
        'pytest-cov',
        'wily',
        'codecov',
    )

    if BasicFunctions.osName() == 'windows':
        install('pypiwin32')
