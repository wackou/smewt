#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
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

from os.path import join, split, basename
import re

def splitFilename(filename):
    root, path = split(filename)
    result = [ path ]
    # FIXME: this is a hack... How do we know we're at the root node?
    while len(root) > 1:
        root, path = split(root)
        result.append(path)
    return result

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
