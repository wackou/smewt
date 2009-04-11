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
import os, os.path, fnmatch
import pycurl

def smewtDirectory(*args):
    return os.path.join(os.getcwd(), *args)

def splitFilename(filename):
    root, path = os.path.split(filename)
    result = [ path ]
    # FIXME: this is a hack... How do we know we're at the root node?
    while len(root) > 1:
        root, path = os.path.split(root)
        result.append(unicode(path))
    return result

class GlobDirectoryWalker:
    # a forward iterator that traverses a directory tree

    def __init__(self, directory, patterns = ['*']):
        self.stack = [directory]
        self.patterns = patterns
        self.files = []
        self.index = 0

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
                if os.path.isdir(fullname):
                    self.stack.append(fullname)
                for pattern in self.patterns:
                    if fnmatch.fnmatch(file, pattern):
                        return fullname


class CurlDownloader:
    def __init__(self):
        self.contents = ''
        self.c = pycurl.Curl()

    def callback(self, buf):
        self.contents += buf

    def get(self, url):
        self.contents = ''
        c = self.c
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, self.callback)
        c.setopt(c.COOKIEFILE, '')
        c.setopt(c.FOLLOWLOCATION, 1)
        c.perform()

    def __del__(self):
        self.c.close()
