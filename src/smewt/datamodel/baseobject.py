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

import logging

log = logging.getLogger('smewt.datamodel.Ontology')

class BaseObject(object):
    """Derive from this class to define an ontology domain.

    Instantiating an object through derived classes should return an ObjectNode and
    not a derived class instance.

    You should define the following class variables in derived classes:

    1- 'schema' which is a map of property names to their respective types
    ex: schema = { 'epNumber': int,
                   'title': str
                   }

    2- 'reverseLookup' are used to indicated the name to be used for
            # the property name when following a relationship between objects in the other direction
            # ie: if Episode(...).series == Series('Scrubs'), then we define automatically
            # a way to access the Episode() from the pointed to Series() object.
            # with 'series' -> 'episodes', we then have:
            # Series('Scrubs').episodes = [ Episode(...), Episode(...) ]
            # reverseLookup needs to be defined for each property which is a Node object

    3- 'valid' which is the list of properties a node needs to have to be able to be considered
               as a valid instance of this class

    4- 'unique' which is the list of properties that form a primary key

    5- 'order' (optional) which is a list of properties you always want to see in front for debug msgs

    6- 'converters' (optional), which is a dictionary from property name to
       a pair of functions that are able to serialize/deserialize this property to/from a unicode string.


    NB: this class only has class methods, because as instantiated objects are ObjectNodes instances,
    we could not even call member functions from this subclass.
    """
    # this should be set to the used ObjectNode class (ie: ObjectNode or PersistentObjectNode)
    _objectNodeClass = type(None)

    schema = {}
    valid = []
    reverseLookup = []
    order = []
    converters = {}

    def __init__(self, graph, basenode = None, **kwargs):
        if basenode is None:
            # MemoryObjectGraph._objectNodeImpl == MemoryObjectNode
            self._node = graph._objectNodeImpl(graph, **kwargs)
        else:
            if isinstance(basenode, BaseObject):
                basenode = basenode._node

            # if basenode is already in this graph, no need to make a copy of it
            if basenode._graph is graph:
                self._node = basenode
            else:
                self._node = graph._objectNodeImpl(graph, **basenode.todict())
            self._node.update(kwargs)
        #if not isinstance(basenode, BaseObject) and not isinstance(basenode, BaseObject._objectNodeClass):
        #    raise TypeError("basenode should be an instance of BaseObject or %s" % _objectNodeClass.__name__)
        #self._node = basenode or ObjectNode(self.__class__, **kwargs)

    def isinstance(self, cls):
        if cls is BaseObject._objectNodeClass:
            return True
        return isinstance(self, cls)

    def __getattr__(self, name):
        return getattr(self._node, name)

    def __setattr__(self, name, value):
        if name == '_node':
            object.__setattr__(self, name, value)
        else:
            setattr(self._node, name, value)

    def __eq__(self, other):
        # TODO: should allow comparing a BaseObject with an ObjectNode
        if not isinstance(other, BaseObject): return False

        if self._node == other._node: return True
        # FIXME: this could lead to cycles or very long chained __eq__ calling on properties
        return self.items() == other.items()

    @classmethod
    def className(cls):
        return cls.__name__

    @classmethod
    def parentClass(cls):
        return cls.__mro__[1]

    def isUnique(self):
        """Return whether all unique properties (as defined by the class) of the ObjectNode
        are non-null."""
        for prop in self.__class__.unique:
            if prop not in self._node:
                return False
        return True

    def uniqueKey(self):
        """Return a tuple containing an unique identifier (inside its class) for this instance.
        If some unique fields are not specified, None will be put instead."""
        return tuple(self.get(k) for k in self._class.unique)



    '''
    def oops__new__(cls, **kwargs):
        print 'creating node'
        result = ObjectNode(cls, **kwargs)
        print 'node created'
        # we also need to call the intended constructor for the object, the one defined
        # in the class definition. It will not receive any other arguments than the fully
        # constructed ObjectNode
        cls.__init__(result)
        print 'node initialized'

        # BaseObject shouldn't need to be in the valid classes as it doesn't define
        # anything, and removing it here allows to avoid import dependency problems
        print 'RC', result._classes
        try: result._classes.remove(BaseObject)
        except ValueError: pass
        print 'RC', result._classes

        return result
    '''

