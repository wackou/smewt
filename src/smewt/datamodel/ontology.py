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

import weakref
import logging

log = logging.getLogger('smewt.datamodel.Ontology')

# use dict here for fast text based access (when instantiating objects through a graph, for instance)
_classes = {}
_graphs = weakref.WeakValueDictionary()


def validateClassDefinition(cls):
    BaseObject = _classes['BaseObject']

    if not issubclass(cls, BaseObject):
        raise TypeError, "'%s' needs to derive from ontology.BaseObject" % cls.__name__

    # Note: voluntarily omit to put str as allowed types, unicode is much better
    #       and it will save us a *lot* of trouble
    # Note: list should only be list of literal values
    # TODO: add datetime
    validTypes = [ unicode, int, long, float, list, BaseObject ]

    def checkPresent(cls, var, ctype):
        try:
            value = getattr(cls, var)
        except AttributeError:
            raise TypeError("Your subclass '%s' should define the '%s' class variable as a '%s'" % (cls.__name__, var, ctype.__name__))
        if type(value) != ctype:
            raise TypeError("Your subclass '%s' defines the '%s' class variable as a '%s', but it should be of type '%s'" % (cls.__name__, var, type(value).__name__, ctype.__name__))

    def checkSchemaSubset(cls, var):
        checkPresent(cls, var, list)
        for prop in getattr(cls, var):
            if not prop in cls.schema:
                raise TypeError("In '%s': when defining '%s', you used the '%s' variable, which is not defined in the schema" % (cls.__name__, var, prop))

    # validate the schema is correctly defined
    checkPresent(cls, 'schema', dict)
    for name, ctype in cls.schema.items():
        if not isinstance(name, str) or not any(issubclass(ctype, dtype) for dtype in validTypes):
            raise TypeError("In '%s': the schema should be a dict of 'str' to either one of those accepted types (or a subclass of them): %s'" % (cls.__name__, ', '.join("'%s'" % c.__name__ for c in validTypes)))

    # all the properties defined as subclasses of BaseObject need to have an
    # associated reverseLookup entry
    checkPresent(cls, 'reverseLookup', dict)
    objectProps = [ name for name, ctype in cls.schema.items() if issubclass(ctype, BaseObject) ]
    diff = set(cls.reverseLookup.keys()).symmetric_difference(set(objectProps))
    if diff:
        raise "In '%s': you should define exactly one reverseLookup name for each property in your schema that is a subclass of BaseObject, different ones: %s" % (cls.__name__, ', '.join("'%s'" % c for c in diff))

    checkSchemaSubset(cls, 'valid')
    checkSchemaSubset(cls, 'unique')
    checkSchemaSubset(cls, 'order')
    # TODO: validate converters


def register(*args):
    # can only register classes which are subclasses of our BaseObject class.
    for cls in args:
        if cls.__name__ in _classes:
            if cls == _classes[cls.__name__]:
                print 'INFO: class %s already registered' % cls.__name__
                return

            print 'WARNING: overriding previous definition of class %s' % cls.__name__

        validateClassDefinition(cls)
        _classes[cls.__name__] = cls

    # revalidate all ObjectNodes in all registered Graphs
    for g in _graphs.values():
        g.revalidateObjects()

def registerGraph(graph):
    _graphs[id(graph)] = graph

def getClass(className):
    """Returns the ObjectNode class object given its name."""
    try:
        return _classes[className]
    except:
        raise ValueError, 'Class "%s" has not been registered with the OntologyManager' % className

def classNames():
    return _classes.keys()
