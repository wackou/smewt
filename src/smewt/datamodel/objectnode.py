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
import ontology
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
    given as a string (ie: node.isinstance('Movie')) to avoid too many importing headaches.
    """

    def __init__(self, graph):
        self._graph = graph
        self.updateValidClasses()

    def isValidInstance(self, cls):
        for prop in cls.valid:
            if prop not in self:
                return False

            if True: # graphType == 'STATIC'
                if type(getattr(self, prop)) != cls.schema[prop]:
                    return False

        return True

    def invalidProperties(self, cls):
        invalid = []
        for prop in cls.valid:
            if prop not in self:
                invalid.append("property '%s' is missing" % prop)
                continue

            if type(getattr(self, prop)) != cls.schema[prop]:
                invalid.append("property '%s' is of type '%s', but should be of type '%s'" %
                               (prop, type(getattr(self, prop)).__name__, cls.schema[prop].__name__))

        return '\n'.join(invalid)

    def updateValidClasses(self):
        self._classes = [ cls for cls in ontology._classes.values() if self.isValidInstance(cls) ]

        log.debug('valid classes for %s:\n  %s' % (self.toString(), self._classes))

    def isinstance(self, cls):
        # this should deal with inheritance correctly, as if this node is a correct instance
        # of a derived class, it should also necessarily be a correct instance of a parent class
        # TODO: for this to be true, we must make sure that derived classes in the ontology
        #       do not override properties defined in a parent class
        if cls in self._classes:
            return True

        # maybe we changed some value that now made this into a valid class, just revalidate
        # to make sure
        # TODO: this should probably go into setattr to revalidate in realtime (only for
        #       arguments which are not part of the schema, for optimization)
        self.updateValidClasses()

        return cls in self._classes

    def __eq__(self, other):
        # This should implement identity of nodes, not properties equality (this should be done
        # in the BaseObject instance)
        # TODO: we should also allow comparison with instances of BaseObject directly
        raise NotImplementedError
        # TODO: maybe like that? return hash(self) == hash(other)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # TODO: verify me
        #return hash((self._class, self.uniqueKey()))
        #return id(self)
        # TODO: look at comment in __eq__ method.
        raise NotImplementedError

    def __str__(self):
        return self.toString().encode('utf-8')

    def __unicode__(self):
        return self.toString()

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

    def __iter__(self):
        for prop in self.keys():
            yield prop


    ### manipulation methods

    def update(self, props):
        """Update this ObjectNode properties with the ones contained in the given dict.
        Should also allow instances of other ObjectNode, or even BaseObject. (or should we
        have an API like n.update(dict(other.items())? )"""
        raise NotImplementedError

    def updateNew(self, other):
        """Update this ObjectNode properties with the only other ones it doesn't have yet."""
        raise NotImplementedError

    def toString(self):
        return u'ObjectNode(%s)' % (', '.join([ u'%s=%s' % (k, v) for k, v in self.items() ]))

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
