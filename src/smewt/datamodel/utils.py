#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2009 Nicolas Wack <wackou@gmail.com>
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

import ontology

def tolist(obj):
    if    obj is None: return []
    elif  isinstance(obj, list): return obj
    else: return [ obj ]


def toresult(lst):
    """Take a list and return a value depending on the number of elements in that list:
     - 0 elements -> return None
     - 1 element  -> return the single element
     - 2 or more elements -> returns the original list."""
    if    not lst: return None
    elif  len(lst) == 1: return lst[0]
    else: return lst

def toIterator(obj):
    for i in tolist(obj):
        yield i

def isOf(name):
    return 'is%sOf' % (name[0].upper() + name[1:])

def isLiteral(value):
    return type(value) in ontology.validLiteralTypes

def reverseLookup(d, cls):
    return [ (name, value, cls.reverseLookup.get(name) or isOf(name)) for name, value in d.items() ]
