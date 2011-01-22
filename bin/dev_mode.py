#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re

if len(sys.argv) != 2:
    print 'Error: you need to specify a version number for the make_release script to work. Aborting...'
    sys.exit(1)


VERSION = sys.argv[1]

# write version number to file
sinit = open('smewt/__init__.py').read()
sinit = re.sub('__version__ =.*', '__version__ = \'%s\'' % VERSION, sinit)
sinit = re.sub('APP_NAME = .*', 'APP_NAME = \'Smewt-dev\'', sinit)
open('smewt/__init__.py', 'w').write(sinit)


# replace logging function call in smewg
smewg = open('bin/smewg').read()
logfunc = [ l for l in open('utils/slogging.py') if l[0] != '#' ]
smewg = smewg.replace(''.join(logfunc) + '\nsetupLogging()\n',
                      '''from utils.slogging import setupLogging
setupLogging()''', )
open('bin/smewg', 'w').write(smewg)

print 'Successfully switched to development version ' + VERSION
