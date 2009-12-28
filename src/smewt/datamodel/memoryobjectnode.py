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

from smewt.base.textutils import toUtf8
import logging

log = logging.getLogger('smewt.datamodel.ObjectNode')

class ObjectNode(object):
    """An ObjectNode is a nice and useful mix between an OOP object and a node in a graph.

    An ObjectNode behaves in the following way:
     - it can have any number of named properties, of any type (literal type or another ObjectNode)
     - it implements dotted attribute access.
     - it still has a class which "declares" a schema of standard properties and their types, like a normal object in OOP
     - it can be validated against that schema (ie: do the actual properties have the same type as those declared in the class definition)
     - setting attributes can be validated for type in real-time
     - it has primary properties, which are used as primary key for identifying ObjectNodes or for indexing purposes

    ObjectNodes should implement different types of equalities:
      - identity: both refs point to the same node in the ObjectGraph
      - all their properties are equal (same type and values)
      - all their standard properties are equal
      - only their primary properties are equal

    To be precise, ObjectNodes use a type system based on relaxed type classes
    (http://en.wikipedia.org/wiki/Type_classes)
    where there is a standard object hierarchy, but an ObjectNode can be of various distinct
    classes at the same time.

    As this doesn't fit exactly with python's way of doing things, class value should be tested
    using the ObjectNode.isinstance(class) and ObjectNode.issubclass(class, subclass) methods,
    instead of the usual isinstance(obj, class) function.

    Classes which have been registered in the global ontology can also be tested with their basename
    given as a string (ie: node.isinstance('Movie'))
    """

    def __init__(self, cls, **kwargs):
        self._graph = None
        # TODO: find all classes in the graph ontology that are valid for this node
        self._classes = [ cls ]
        self._props = kwargs

    def isinstance(self, cls):
        return any(issubclass(c, cls) for c in self._classes)

    def __eq__(self, other):
        if not isinstance(other, ObjectNode): return False
        return self._props == other._props

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # TODO: verify me
        #return hash((self._class, self.uniqueKey()))
        return id(self)

    def __str__(self):
        return self.toShortString()

    ### Acessing properties methods

    def __getattr__(self, name):
        # TODO: this should go into the PersistentObjectNode
        #if name == '_node':
        #    return self.__dict__[name]

        print 'getattr'
        try:
            return self._props[name]
        except:
            # if attribute was not found, look whether it might be a reverse attribute
            if name.startswith('is_') and name.endswith('_of'):
                if self._graph is None:
                    raise AttributeError, 'Cannot get reverse attribute of node for which no Graph has been set'
                return self._graph.reverseLookup(self, name[3:-3])

            # TODO: find valid classes which have a method with a corresponding name
            classes = [ c for c in self._classes if name in c.__dict__ ]


            raise AttributeError, name

    def get(self, name):
        """Returns the given property or None if not found."""
        try:
            # First look for literal value properties
            return getattr(self, name)
        except AttributeError:
            return None
            # TODO: PersistentObjectNode impl:
            # if no literal was found, try to find another ObjectNode
            #result = list(self._node.relationships(name))
            #if not result: return None # raise AttributeError
            #if len(result) == 1: return wrapNode(result[0].end)
            #return result

    def __setattr__(self, name, value):
        if name in [ '_graph', '_classes', '_props' ]:
            object.__setattr__(self, name, value)
        else:
            #setting attribute should validate that the attribute stayed of the same type
            # as what is defined in its schema
            for c in self._classes:
                if name in c.schema:
                    if type(value) != c.schema[name]:
                        raise ValueError, "The '%s' attribute is of type '%s' but you tried to assign it a '%s'" % (name, c.schema[name], type(value))
                    else:
                        break # exit earlier from loop, type is validated

            self._props[name] = value

    ### Container methods

    def keys(self):
        # TODO: should return a generator
        return self._props.keys()

    def values(self):
        # TODO: should return a generator
        return self._props.values()

    def items(self):
        # TODO: should return a generator
        return self._props.items()

    ### Validation against a class schema

    def isValid(self):
        """Return whether all the ObjectNode properties which exist in the class schema have the same
        type as what is defined."""
        try:
            for prop in self._class.schema.keys():
                if prop in self._props and type(self._props[prop]) != self._class.schema[prop]:
                    return False
        except KeyError:
            return False

        return True

    def isUnique(self):
        """Return whether all unique properties (as defined by the class) of the ObjectNode
        are non-null."""
        for prop in self._class.unique:
            if prop not in self._props or self._props[prop] is None:
                return False
        return True

    def uniqueKey(self):
        """Return a tuple containing an unique identifier (inside its class) for this instance.
        If some unique fields are not specified, None will be put instead."""
        return tuple(self.get(k) for k in self._class.unique)


    ### manipulation methods

    def update(self, other):
        """Update this ObjectNode properties with all the other ones."""
        self._props.update(other._props)

    def updateNew(self, other):
        """Update this ObjectNode properties with the only other ones it doesn't have yet."""
        for name, value in other._props.items():
            if name not in self._props:
                self._props[name] = value

    def orderedProperties(self):
        """Returns the list of properties ordered using the defined order in the subclass.

        NB: this should be replaced by using an OrderedDict."""
        result = []
        propertyNames = self._props.keys()

        for p in self._class.order:
            if p in propertyNames:
                result.append(p)
                propertyNames.remove(p)

        return result + propertyNames

    def toShortString(self):
        return '%s(%s)' % (self._class.__name__,
                           ', '.join([ '%s=%s' % (k, v) for k, v in self._props.items() ]))

    def toFullString(self, tabs = 0):
        tabstr = 4 * tabs * ' '
        tabstr1 = 4 * (tabs+1) * ' '
        result = ('valid ' if self.isValid() else 'invalid ') + self._class.__name__ + ' : {\n'

        schema = self._class.schema
        for propname in self.orderedProperties():
            if propname in schema and isinstance(self._props[propname], ObjectNode):
                s = self._props[propname].toString(tabs = tabs+1)
            else:
                s = toUtf8(self._props[propname])
            result += tabstr1 + '%-20s : %s\n' % (propname, s)

        return result + tabstr + '}'

