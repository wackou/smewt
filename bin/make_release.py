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
sinit = re.sub('APP_NAME = .*', 'APP_NAME = \'Smewt\'', sinit)
sinit = re.sub('SINGLE_APP_PORT = .*', 'SINGLE_APP_PORT = 8357', sinit)
open('smewt/__init__.py', 'w').write(sinit)

setup = open('setup.py').read()
setup = re.sub('      version =.*', '      version = \'%s\',' % VERSION, setup)
open('setup.py', 'w').write(setup)

nsis = open('packaging/win32/smewt.nsi').read()
nsis = re.sub('!define VERSION .*', '!define VERSION  \'%s\'' % VERSION, nsis)
open('packaging/win32/smewt.nsi', 'w').write(nsis)



# replace logging function call in smewg
smewg = open('bin/smewg').read()

#smewg = re.sub('\nMAIN_LOGGING_LEVEL =.*', '\nMAIN_LOGGING_LEVEL = logging.WARNING', smewg)
smewg = re.sub('\nMAIN_LOGGING_LEVEL =.*', '\nMAIN_LOGGING_LEVEL = logging.INFO', smewg)
smewg = re.sub('\nLOGGING_TCP_PORT =.*', '\nLOGGING_TCP_PORT = 9020', smewg)
smewg = re.sub('$import logging.handlers', '#import logging.handlers', smewg)
smewg = re.sub(r'$(logging.getLogger\(\).addHandler\(logging.handlers.SocketHandler.*)',
               r'#\1', smewg)
smewg = re.sub(r' mainMenu.addAction\(self.logviewAction\)',
               r' #mainMenu.addAction(self.logviewAction)', smewg)

logfunc = [ l for l in open('utils/slogging.py') if l[0] != '#' ]
smewg = smewg.replace('''from utils.slogging import setupLogging
setupLogging()''', ''.join(logfunc) + '\nsetupLogging(%s)\n' % ('colored=False' if sys.platform == 'darwin' else ''))

open('bin/smewg', 'w').write(smewg)


if COMMIT:
    os.system('git commit -a -m "Tagged %s release"' % VERSION)
    os.system('git tag ' + VERSION)


    # generate and upload package to PyPI
    os.system('python setup.py sdist upload')

else:
    os.system('python setup.py sdist')

print 'Successfully made release ' + VERSION
if not COMMIT:
    print 'No files have been committed. To commit, please call this script with the "-f" parameter.'
