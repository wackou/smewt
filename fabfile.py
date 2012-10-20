#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
from fabric.api import *


def up(path):
    return os.path.split(path)[0]

SMEWT_ROOT = up(os.path.abspath(__file__))

SMEWT_ROOT_PARENT = up(SMEWT_ROOT)

# first add paths to local smewt and pygoo repositories
relative_modules = [ 'smewt',
                     #'pygoo',
                     'guessit',
                     'subliminal'
                     ]

py_path = [ os.path.join(SMEWT_ROOT_PARENT, module)
            for module in relative_modules ]

py_path = 'PYTHONPATH=%s:$PYTHONPATH ' % (':'.join(py_path))


@task
def profile():
    """Run Smewt and profile it, write the resulting data into /tmp/profstats."""
    local(py_path + 'python -m cProfile -o /tmp/profstats bin/smewg')
    print 'Wrote profile results in /tmp/profstats'
    print 'You can visualize them with "runsnake /tmp/profstats"'

@task(default=True)
def smewt():
    """Run Smewt."""
    local(py_path + 'python bin/smewg')

@task
def make_release(version):
    print 'Making release', version

@task
def change_version_number(version):
    # write version number to files
    sinit = open('smewt/__init__.py').read()
    sinit = re.sub('__version__ =.*', '__version__ = \'%s\'' % version, sinit)
    sinit = re.sub('APP_NAME = .*', 'APP_NAME = \'Smewt-dev\'', sinit)
    sinit = re.sub('SINGLE_APP_PORT = .*', 'SINGLE_APP_PORT = 8358', sinit)
    open('smewt/__init__.py', 'w').write(sinit)

    setup = open('setup.py').read()
    setup = re.sub('      version =.*', '      version = \'%s\',' % version, setup)
    open('setup.py', 'w').write(setup)

    nsis = open('packaging/win32/smewt.nsi').read()
    nsis = re.sub('!define VERSION .*', '!define VERSION  \'%s\'' % version, nsis)
    open('packaging/win32/smewt.nsi', 'w').write(nsis)


# TODO: task:
#  - clear config
#  - save config %s
#  - restore config %s
#  - list configs
#  - delete config %s
