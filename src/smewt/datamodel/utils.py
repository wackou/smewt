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

import types
import ontology

def tolist(obj):
    if    obj is None: return []
    elif  isinstance(obj, list): return obj
    else: return [ obj ]


def multiIsInstance(value, cls):
    if isinstance(value, list):
        return all(isinstance(v, cls) for v in value)
    elif isinstance(value, types.GeneratorType):
        # we can't touch the generator otherwise the values will be lost
        return True # NB: this behaviour is debatable
    else:
        return isinstance(value, cls)



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
    return (type(value) in ontology.validLiteralTypes or
            value is None or # TODO: is None could be checked here for validity in the schema
            any(multiIsInstance(value, cls) for cls in ontology.validLiteralTypes))


def checkClass(name, value, schema, converters = {}):
    """This function also converts BaseObjects to nodes after having checked their class."""
    def tonodes(v):
        ontology.importClass('BaseObject')
        if isinstance(v, BaseObject):
            return v._node
        elif isinstance(v, list) and v != [] and isinstance(v[0], BaseObject):
            return (n._node for n in v)
        else:
            return v

    if name not in schema or multiIsInstance(value, schema[name]):
        return tonodes(value)

    # try to autoconvert a string to int or float
    if (isinstance(value, unicode) or isinstance(value, str)) and schema[name] in [ int, float ]:
        try:
            return schema[name](value)
        except ValueError:
            pass

    # try to autoconvert a string to a unicode
    if isinstance(value, str) and schema[name] in [ unicode ]:
        try:
            return unicode(value)
        except ValueError:
            pass

    # TODO: use specified converters, when available

    raise TypeError, "The '%s' attribute is of type '%s' but you tried to assign it a '%s'" % (name, schema[name], type(value))


def reverseLookup(d, cls):
    """Returns a list of tuples used mostly for node creation, where BaseObjects have been replaced with their nodes.
    They are triples of (name, literal value or node generator, reverseName).
    This also checks for type validity and converts the values if they have type converters.
    string -> unicode, string -> int  and  string -> float  are done automatically."""
    return [ (name,
              checkClass(name, value, cls.schema, cls.converters),
              cls.reverseLookup.get(name) or isOf(name))
             for name, value in d.items() ]
