#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print 'Error: you need to specify a version number for the make_release script to work. Aborting...'
    sys.exit(1)

VERSION = sys.argv[1]
COMMIT = False

if len(sys.argv) == 3:
    if sys.argv[1] == '-f':
        VERSION = sys.argv[2]
        COMMIT = True
    elif sys.argv[2] == '-f':
        VERSION = sys.argv[1]
        COMMIT = True
    else:
        print 'Invalid parameters: ' + ' '.join(sys.argv)
        sys.exit(1)


# write version number to files
sinit = open('smewt/__init__.py').read()
sinit = re.sub('__version__ =.*', '__version__ = \'%s\'' % VERSION, sinit)
sinit = re.sub('APP_NAME = .*', 'APP_NAME = \'Smewt-dev\'', sinit)
sinit = re.sub('SINGLE_APP_PORT = .*', 'SINGLE_APP_PORT = 8358', sinit)
open('smewt/__init__.py', 'w').write(sinit)

setup = open('setup.py').read()
setup = re.sub('      version =.*', '      version = \'%s\',' % VERSION, setup)
open('setup.py', 'w').write(setup)

nsis = open('packaging/win32/smewt.nsi').read()
nsis = re.sub('!define VERSION .*', '!define VERSION  \'%s\'' % VERSION, nsis)
open('packaging/win32/smewt.nsi', 'w').write(nsis)


# replace logging function call in smewg
smewg = open('bin/smewg').read()

smewg = re.sub('\nMAIN_LOGGING_LEVEL =.*', '\nMAIN_LOGGING_LEVEL = logging.INFO', smewg)
smewg = re.sub('\nLOGGING_TCP_PORT =.*', '\nLOGGING_TCP_PORT = 9025', smewg)

logfunc = [ l for l in open('utils/slogging.py') if l[0] != '#' ]
smewg = smewg.replace(''.join(logfunc) + '\nsetupLogging(%s)\n' % ('colored=False' if sys.platform == 'darwin' else ''),
                      '''from utils.slogging import setupLogging
setupLogging()''', )

open('bin/smewg', 'w').write(smewg)

if COMMIT:
    os.system('git commit -a -m "Switched back to development version "' + VERSION)

print 'Successfully switched to development version ' + VERSION

if not COMMIT:
    print 'No files have been committed. To commit, please call this script with the "-f" parameter.'
