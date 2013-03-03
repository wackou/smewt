#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path
import re
import sys
from fabric.api import *


def up(path):
    return os.path.split(path)[0]

SMEWT_ROOT = up(os.path.abspath(__file__))

SMEWT_ROOT_PARENT = up(SMEWT_ROOT)

# first add paths to local smewt and pygoo repositories
import_modules = [ '.',
                   '3rdparty/pygoo',
                   '3rdparty/guessit',
                   '3rdparty/subliminal',
                   '3rdparty/webkit2png'
                   ]

py_path = [ os.path.join(SMEWT_ROOT, module)
            for module in import_modules ]

py_path = 'PYTHONPATH=%s:$PYTHONPATH ' % (':'.join(py_path))

# add path for webkit2png
py_path = 'PATH=3rdparty/webkit2png/scripts:$PATH ' + py_path

@task
def update_yappi():
    try:
        local('pip uninstall --yes yappi')
    except:
        pass

    with lcd('../yappi'):
        local('rm -fr dist')
        local('python setup.py sdist')

    local('pip install ../yappi/dist/*.gz')

@task
def profile():
    """Run Smewt and profile it, print the resulting data to stdout."""
    local(py_path + 'python -m smewt.main --profile')

@task
def clean_pyc():
    """Removes all the *.pyc files found in the repository"""
    local('find . -iname "*.pyc" -delete')

@task
def python(arg1):
    local(py_path + 'python ' + arg1)

@task
def ipython():
    local(py_path + 'ipython')

@task(default=True)
def smewt():
    """Run Smewt."""
    local(py_path + 'python -m smewt.main')


def replace_in_file(filename, rexps):
    with open(filename) as f:
        text = f.read()
    for rexp, subst in rexps:
        text = re.sub(rexp, subst, text)
    with open(filename, 'w') as f:
        f.write(text)

@task
def change_version_number(version, mode='dev'):
    dev = True
    colored_logging = True

    if mode.startswith('dev'):
        app = 'Smewt-dev'
        port = 8358
        logging_level = 'INFO'
        logging_port = 9025

    elif mode.startswith('rel'):
        dev = False
        app = 'Smewt'
        port = 8357
        logging_level = 'INFO'
        logging_port = 9020
        if sys.platform == 'darwin':
            colored_logging = False

    else:
        print 'Error: invalid mode %s. Should be dev or release' % mode
        sys.exit(1)


    print 'Changing version number to %s, mode=%s' % (version, 'development' if dev else 'release')

    # write version number to files
    replace_in_file('smewt/__init__.py',
                    [ ('__version__ =.*',      "__version__ = '%s'" % version),
                      ('APP_NAME = .*',        "APP_NAME = '%s'" % app),
                      ('SINGLE_APP_PORT = .*', 'SINGLE_APP_PORT = %d' % port) ])

    replace_in_file('setup.py',
                    [ ('version =.*', "version = '%s'," % version) ])

    replace_in_file('packaging/win32/smewt.nsi',
                    [ ('!define VERSION .*', "!define VERSION  '%s'" % version) ])

    comment_patterns = [ ('\n', 'import logging.handlers'),
                         ('\n', r'logging.getLogger\(\).addHandler\(logging.handlers.SocketHandler.*'),
                         (' ', r'mainMenu.addAction\(self.logviewAction\)') ]

    if dev:
        # uncomment everything
        patterns = [ ('#'+'('+p+')', r'\1') for sep, p in comment_patterns ]
    else:
        # comment everything, logview is too heavy for a release build
        patterns = [ (sep+'('+p+')', sep+r'#\1') for sep, p in comment_patterns ]

    replace_in_file('bin/smewg',
                    [ ('\nMAIN_LOGGING_LEVEL =.*',
                       '\nMAIN_LOGGING_LEVEL = logging.%s' % logging_level),
                      ('\nLOGGING_TCP_PORT =.*',
                       '\nLOGGING_TCP_PORT = %d' % logging_port),
                      (r'setupLogging\(.*',
                       'setupLogging(colored=%s)' % colored_logging) ] + patterns)


@task
def install(version):
    change_version_number(version, mode='release')
    # TODO: deactivate the virtualenv?
    #local('python setup.py install')

@task
def make_release(version, commit=False):
    change_version_number(version, mode='release')
    if commit:
        local('git commit -a -m "Tagged %s release"' % version)
        local('git tag %s' % version)

        # generate and upload package to PyPI
        local('python setup.py sdist upload')
    else:
        local('python setup.py sdist')

    print 'Successfully made release ' + version
    if not commit:
        print 'No files have been committed. To commit, please call this script with the "-f" parameter.'


@task
def dev_mode(version, commit=False):
    change_version_number(version, mode='dev')
    if commit:
        local('git commit -a -m "Switched back to development version %s"' % VERSION)

    print 'Successfully switched to development version ' + version

    if not commit:
        print 'No files have been committed. To commit, please call this script with the "-f" parameter.'


# TODO: task:
#  - clear config
#  - save config %s
#  - restore config %s
#  - list configs
#  - delete config %s
