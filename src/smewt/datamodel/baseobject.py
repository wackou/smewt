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

from objectnode import ObjectNode
from ontology import Schema
import logging

log = logging.getLogger('smewt.datamodel.Ontology')


def getNode(node):
    if isinstance(node, ObjectNode):
        return node
    elif isinstance(node, BaseObject):
        return node._node
    else:
        raise TypeError("Given object is not an ObjectNode or BaseObject instance")

def checkClass(name, value, schema):
    if name in schema and type(value) != schema[name]:
        raise TypeError, "The '%s' attribute is of type '%s' but you tried to assign it a '%s'" % (name, schema[name], type(value))


class BaseObject(object):
    """Derive from this class to define an ontology domain.

    You should define the following class variables in derived classes:

    1- 'schema' which is a dict of property names to their respective types
        ex: schema = { 'epNumber': int,
                       'title': unicode
                       }

    2- 'reverseLookup' which is a dict used to indicate the name to be used for the property name
                       when following a relationship between objects in the other direction.
                       ie: if Episode(...).series == Series('Scrubs'), then we define automatically
                       a way to access the Episode() from the pointed to Series() object.
                       with { 'series': 'episodes' }, we then have:
                       Series('Scrubs').episodes = [ Episode(...), Episode(...) ]
                       reverseLookup must be defined for each property which is a Node object

    3- 'valid' which is the list of properties a node needs to have to be able to be considered
               as a valid instance of this class

    4- 'unique' which is the list of properties that form a primary key

    5- 'order' (optional) which is a list of properties you always want to see in front for debug msgs
               by default, this will be set to the 'valid' variable

    6- 'converters' (optional), which is a dictionary from property name to a pair of functions
                    that are able to serialize/deserialize this property to/from a unicode string.

    """

    # TODO: remove those variables which definition should be mandatory
    schema = Schema({})
    reverseLookup = {}
    valid = []
    unique = []
    order = []
    converters = {}

    # This variable works just like the 'schema' one, except that it only contains properties which have been defined
    # as a result of the reverseLookup names of other classes
    #_implicitSchema = {}

    def __init__(self, basenode = None, graph = None, **kwargs):
        if graph is None and basenode is None:
            raise ValueError('You need to specify either a graph or a base node when instantiating a %s' % self.__class__.__name__)

        # just to make sure, while developing. This should probably be removed in a stable version
        if (#(graph is not None and not isinstance(graph, ObjectGraph)) or
            (basenode is not None and not (isinstance(basenode, ObjectNode) or
                                           isinstance(basenode, BaseObject)))):
                print BaseObject
                print type(basenode)
                print isinstance(basenode, BaseObject)
                raise ValueError('graph: %s - node: %s' % (type(graph), type(basenode)))

        if basenode is None:
            # if no basenode is given, we need to create a new node
            self._node = graph.createNode(**kwargs)

        else:
            basenode = getNode(basenode)

            # if basenode is already in this graph, no need to make a copy of it
            # if graph is None, we might just be making a new instance of a node, so it's in the same graph as well
            if graph is None or graph is basenode._graph:
                self._node = basenode
            else:
                # FIXME: this should use Graph.addNode to make sure it is correctly added (with its linked nodes and all)
                self._node = graph.createNode(**dict(basenode.items()))

        # we can only give ObjectNodes to a node's method arguments
        #for name, value in kwargs.items():
        #    if isinstance(value, BaseObject):
        #        kwargs[name] = value._node
        #self._node.update(kwargs)
        self.update(kwargs)

        # make sure that the new instance we're creating is actually a valid one
        if not self._node.isValidInstance(self.__class__):
            raise TypeError("Cannot instantiate a valid instance of %s because:\n%s" %
                            (self.__class__.__name__, self._node.invalidProperties(self.__class__)))


    def __getattr__(self, name):
        result = getattr(self._node, name)

        # if the result is an ObjectNode, wrap it with the class it has been given in the class schema
        # if it was not in the class schema, simply returns an instance of BaseObject
        # FIXME: make sure that if we return a list of objects, each of them gets converted properly
        if isinstance(result, ObjectNode):
            cls = self.__class__
            if name in cls.schema:
                resultClass = cls.schema[name]
            else:
                resultClass = BaseObject

            return resultClass(basenode = result)

        else:
            return result


    def __setattr__(self, name, value):
        if name == '_node':
            object.__setattr__(self, name, value)
        else:
            cls = self.__class__
            if name in cls.schema._implicit:
                print '-'*10000
                raise ValueError("Implicit properties are read-only (%s.%s)" % (cls.__name__, name))
            checkClass(name, value, cls.schema)

            if isinstance(value, BaseObject):
                value = value._node

            self._node.set(name, value, reverseName = cls.reverseLookup.get(name))


    def __eq__(self, other):
        # TODO: should allow comparing a BaseObject with an ObjectNode?
        if not isinstance(other, BaseObject): return False

        if self._node == other._node: return True
        # FIXME: this could lead to cycles or very long chained __eq__ calling on properties
        return self.explicitItems() == other.explicitItems()

    def __str__(self):
        return self._node.toString(cls = self.__class__).encode('utf-8')

    def explicitItems(self):
        return [ x for x in self.items() if x[0] not in self.__class__.schema._implicit ]

    @classmethod
    def className(cls):
        return cls.__name__

    @classmethod
    def parentClass(cls):
        return cls.__mro__[1]

    def update(self, props):
        for name, value in props.items():
            if isinstance(value, BaseObject):
                value = value._node
                reverseName = self.__class__.reverseLookup.get(name)
            else:
                reverseName = None
            self._node.set(name, value, reverseName)


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


    def orderedProperties(self):
        """Returns the list of properties ordered using the defined order in the subclass.

        NB: this should be replaced by using an OrderedDict."""
        result = []
        propertyNames = list(self._node.keys())

        for p in self.__class__.order:
            if p in propertyNames:
                result.append(p)
                propertyNames.remove(p)

        return result + propertyNames





# force-register BaseObject in the ontology classes (ie: do not use the ontology
# validation stuff, because it needs the ObjectNode to be already registered)
import ontology
ontology._classes['BaseObject'] = BaseObject
