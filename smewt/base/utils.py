#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@gmail.com>
#
# Smewt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Smewt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#



# filename- and network-related functions
import sys, os, os.path, fnmatch,  errno
import pycurl
from PyQt4.QtCore import QSettings, QVariant
import smewt
from pygoo.utils import tolist, toresult

class MethodID(object):
    def __init__(self, filename, module, className, methodName):
        self.filename = filename
        self.module = module
        self.className = className
        self.methodName = methodName

    def __str__(self):
        return 'module: %s - class: %s - func: %s' % (self.module, self.className, self.methodName)

def callerid():
    f = sys._getframe(1)

    filename = f.f_code.co_filename
    module = ''
    className = ''

    try:
        module = f.f_locals['self'].__class__.__module__
        className = f.f_locals['self'].__class__.__name__
    except:
        pass

    methodName = f.f_code.co_name

    return MethodID(filename, module, className, methodName)

def currentPath():
    '''Returns the path in which the calling file is located.'''
    return os.path.dirname(os.path.join(os.getcwd(), sys._getframe(1).f_globals['__file__']))

def makedir(path):
    try:
        os.makedirs(path)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else: raise

def pathToUrl(path):
    if sys.platform == 'win32':
        # perform some drive letter trickery
        return 'localhost/%s:/%s' % (path[0], path[3:])

    return path

def smewtDirectory(*args):
    return os.path.join(currentPath(), '..', '..', *args)

def smewtDirectoryUrl(*args):
    return pathToUrl(smewtDirectory(*args))

def smewtUserDirectory(*args):
    settings = QSettings()
    userdir = unicode(settings.value('user_dir').toString())
    if not userdir:
        if sys.platform == 'win32':
            userdir = os.path.join(os.environ['USERPROFILE'], 'Application Data', 'Smewt')
        else:
            userdir = os.path.dirname(unicode(settings.fileName()))

        settings.setValue('user_dir',  QVariant(userdir))

    userdir = os.path.join(userdir, *args)
    makedir(userdir) # make sure directory exists

    return userdir

def smewtUserDirectoryUrl(*args):
    return pathToUrl(smewtUserDirectory(*args))


def splitFilename(filename):
    root, path = os.path.split(filename)
    result = [ path ]
    while path:
        root, path = os.path.split(root)
        result.append(unicode(path))
    return result


def guessCountryCode(filename):
    '''Given a subtitle filename, tries to guess which languages it contains.
    As a subtitle file can contain multiple subtitles, this function returns a list
    of found languages.'''

    # try to guess language from filename
    langs = [ lang.lower() for lang in filename.split('.') ]

    languages = { 'english': 'en',
                  'french': 'fr',
                  'francais': 'fr',
                  u'fran\xe7ais': 'fr',
                  'spanish': 'es',
                  'espanol': 'es',
                  u'espa\xf1ol': 'es'
                  }

    if len(langs) >= 3:
        l = langs[-2].lower()
        for lang, code in languages.items():
            if l[-2:] == lang[:2] or l[-3:] == lang[:3] or l[-len(lang):] == lang:
                return [ code ]

    # try to look inside the .idx, if it exists
    langs = set()
    if os.path.exists(filename[:-3] + 'idx'):
        lines = open(filename[:-3] + 'idx').readlines()
        for l in lines:
            if l[:3] == 'id:':
                langs.add(l[4:6])

    if langs:
        return list(langs)

    return [ 'unknown' ]

class GlobDirectoryWalker:
    # a forward iterator that traverses a directory tree

    def __init__(self, directory, patterns = ['*'], recursive = True):
        self.stack = [directory]
        self.patterns = patterns
        self.files = []
        self.index = 0
        self.recursive = recursive

    def __getitem__(self, index):
        while True:
            try:
                file = self.files[self.index]
                self.index = self.index + 1
            except IndexError:
                # pop next directory from stack
                self.directory = self.stack.pop()
                self.files = os.listdir(self.directory)
                self.index = 0
            else:
                # got a filename
                fullname = os.path.join(self.directory, file)
                if os.path.isdir(fullname) and self.recursive:
                    self.stack.append(fullname)
                for pattern in self.patterns:
                    if fnmatch.fnmatch(file, pattern):
                        return fullname


class CurlDownloader:
    def __init__(self):
        self.contents = []
        self.c = pycurl.Curl()

    def callback(self, buf):
        self.contents.append(buf)

    def get(self, url):
        self.contents = []
        c = self.c
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, self.callback)
        c.setopt(c.COOKIEFILE, '')
        c.setopt(c.FOLLOWLOCATION, 1)
        c.perform()

        self.contents = ''.join(self.contents)

        return self.contents

    def __del__(self):
        self.c.close()

def curlget(url):
    c = CurlDownloader()
    return c.get(url)
