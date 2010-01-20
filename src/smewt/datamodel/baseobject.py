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

from basicgraph import BasicNode
from objectnode import ObjectNode
from ontology import Schema
from utils import isOf, reverseLookup, toresult
import types
import logging

log = logging.getLogger('smewt.datamodel.Ontology')


def getNode(node):
    if isinstance(node, BasicNode):
        return node
    elif isinstance(node, BaseObject):
        return node._node
    elif isinstance(node, list) and isinstance(node[0], BaseObject):
        return [ n._node for n in node ]
    else:
        raise TypeError("Given object is not an ObjectNode or BaseObject instance")

def toNodes(d):
    result = dict(d)
    for k, v in d.items():
        if isinstance(v, BaseObject):
            result[k] = v._node
    return result

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
        log.debug('BaseObject.__init__: basenode = %s, args = %s' % (basenode, kwargs))
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
            self._node = graph.createNode(reverseLookup(toNodes(kwargs), self.__class__))

        else:
            basenode = getNode(basenode)

            # if basenode is already in this graph, no need to make a copy of it
            # if graph is None, we might just be making a new instance of a node, so it's in the same graph as well
            if graph is None or graph is basenode._graph:
                self._node = basenode
            else:
                self._node = graph.createNode(reverseLookup(basenode, self.__class__)) # TODO: we should be able to construct directly from the other node

            # optimization: avoid revalidating the classes all the time when creating a BaseObject from a pre-existing node
            if kwargs:
                self.update(kwargs)

        # make sure that the new instance we're creating is actually a valid one
        if not self._node.isinstance(self.__class__):
            raise TypeError("Cannot instantiate a valid instance of %s because:\n%s" %
                            (self.__class__.__name__, self._node.invalidProperties(self.__class__)))


    def __getattr__(self, name):
        result = getattr(self._node, name)

        # if the result is an ObjectNode, wrap it with the class it has been given in the class schema
        # if it was not in the class schema, simply returns an instance of BaseObject
        if isinstance(result, types.GeneratorType):
            resultClass = self.__class__.schema.get(name) or BaseObject
            return toresult([ resultClass(basenode = n) for n in result ])

        # FIXME: better test here (although if the graph is consistent it shouldn't be necessary)
        #elif isinstance(result, list) and isinstance(result[0], BasicNode):
        #    resultClass = self.__class__.schema.get(name) or BaseObject
        #    return [ resultClass(basenode = node) for node in result ]

        else:
            return result


    def __setattr__(self, name, value):
        if name == '_node':
            object.__setattr__(self, name, value)
        else:
            self.set(name, value)

    def set(self, name, value, validate = True):
        """Sets the given value to the named property."""
        cls = self.__class__
        if name in cls.schema._implicit:
            raise ValueError("Implicit properties are read-only (%s.%s)" % (cls.__name__, name))

        # objects are statically-typed here; graphType == 'STATIC'
        checkClass(name, value, cls.schema)

        # if we don't have a reverse lookup for this property, default to a reverse name of 'is%(Property)Of'
        reverseName = self.__class__.reverseLookup.get(name) or isOf(name)

        if isinstance(value, BaseObject):
            self._node.set(name, value._node, reverseName, validate)
        else:
            self._node.set(name, value, reverseName, validate)


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
            self.set(name, value, validate = False)
        self._node.updateValidClasses()

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
