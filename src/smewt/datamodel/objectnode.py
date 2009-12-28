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

    def __init__(self, graph, **kwargs):
        self._graph = None
        # TODO: find all classes in the graph ontology that are valid for this node
        self._classes = [ cls ]

    def isValidInstance(self, cls):
        return any(issubclass(c, cls) for c in self._classes)

    def __eq__(self, other):
        if not isinstance(other, ObjectNode): return False
        # TODO: do we want equality of properties of identity of nodes?
        return self.todict() == other.todict()

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
        raise NotImplementedError

    def get(self, name):
        """Returns the given property or None if not found."""
        try:
            return getattr(self, name)
        except AttributeError:
            return None

    def __setattr__(self, name, value):
        if name in [ '_graph', '_classes' ]:
            object.__setattr__(self, name, value)
        else:
            raise NotImplementedError

    ### Container methods

    def keys(self):
        # TODO: should return a generator
        raise NotImplementedError

    def values(self):
        # TODO: should return a generator
        raise NotImplementedError

    def items(self):
        # TODO: should return a generator
        raise NotImplementedError


    ### manipulation methods

    def update(self, other):
        """Update this ObjectNode properties with the given ones."""
        raise NotImplementedError

    def updateNew(self, other):
        """Update this ObjectNode properties with the only other ones it doesn't have yet."""
        raise NotImplementedError

    def toShortString(self):
        return '%s(%s)' % (self._class.__name__,
                           ', '.join([ '%s=%s' % (k, v) for k, v in self.items() ]))

    '''
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
    '''
