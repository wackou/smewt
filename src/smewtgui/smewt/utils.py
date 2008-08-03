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


# regexps-related functions
import re
from base import SmewtException

def matchRegexp(string, regexp):
    match = re.compile(regexp, re.IGNORECASE).search(string)
    if match:
        return match.groupdict()
    raise SmewtException('Does not match regexp')

def matchAllRegexp(string, regexps):
    result = []
    for regexp in regexps:
        match = re.compile(regexp, re.IGNORECASE).search(string)
        if match:
            result.append(match.groupdict())
    return result

def matchAnyRegexp(string, regexps):
    for regexp in regexps:
        result = re.compile(regexp, re.IGNORECASE).search(string)
        if result:
            return result.groupdict()
    return None



# filename-related functions
import os.path,  fnmatch

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
                if os.path.isdir(fullname) and not os.path.islink(fullname):
                    self.stack.append(fullname)
                for pattern in self.patterns:
                    if fnmatch.fnmatch(file, pattern):
                        return fullname
