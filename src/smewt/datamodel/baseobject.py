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

from abstractnode import AbstractNode
from objectnode import ObjectNode
import ontology
from utils import isOf, reverseLookup, toresult, multiIsInstance, checkClass
import types
import logging

log = logging.getLogger('smewt.datamodel.BaseObject')


def getNode(node):
    if isinstance(node, AbstractNode):
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
        elif isinstance(v, list) and (v != [] and isinstance(v[0], BaseObject)):
            result[k] = [ n._node for n in v ]
    return result


# Metaclass to be used for BaseObject so that they are automatically registered in the ontology
class OntologyClass(type):
    def __new__(cls, name, bases, attrs):
        log.info('Creating class: %s' % name)
        if len(bases) > 1:
            raise TypeError('BaseObject does not allow multiple inheritance for class: %s' % name)
        return type.__new__(cls, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        log.info('Initializing class: %s' % name)
        super(OntologyClass, cls).__init__(name, bases, attrs)
        ontology.register(cls, attrs)


    def classVariables(cls):
        # need to return a copy here (we're already messing enough with all those mutable objects around...)
        return (ontology.Schema(cls.schema),
                dict(cls.reverseLookup),
                set(cls.valid),
                set(cls.unique),
                list(cls.order),
                dict(cls.converters))

    def setClassVariables(cls, vars):
        cls.schema = ontology.Schema(vars[0])
        cls.reverseLookup = dict(vars[1])
        cls.valid = set(vars[2])
        cls.unique = set(vars[3])
        cls.order = set(vars[4])
        cls.converters = set(vars[5])


class BaseObject(object):
    """A BaseObject is a statically-typed object which gets its data from an ObjectNode. In that sense, it
    acts like a view of an ObjectNode, and all data assigned to a BaseObject is actually stored in the
    ObjectNode.

    It is possible and inexpensive to create any number of possibly different BaseObject "views" on an
    ObjectNode, which means that you can dynamically interpret an ObjectNode as being an instance of a
    given class (given that it matches the class schema).

    Equality comparison is done by comparing the properties of the nodes, not the identity of the nodes,
    so two BaseObjects wrapping two different nodes in the graph would be equal if their properties are.

    You should derive from this class to define an ontology domain on ObjectGraphs and ObjectNodes.

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


    Apart from having to define the aforementioned class variables, a BaseObject behaves like a python object,
    so that a subclass of BaseObject can also define its own methods and they can be called normally on instances
    of it.
    As an example, you might want to define:

    class Actor:
        def bestMovies(self):
            maxRating = max(movie.rating for movie in self.roles.movie)
            return [ movie for movie in self.roles.movie if movie.rating == maxRating ]


    Note: at the moment, self.roles.movie wouldn't work, so one would have to do so:
    class Actor:
        def bestMovies(self):
            maxRating = max(role.movie.rating for role in self.roles)
            return [ role.movie for role in self.roles if role.movie.rating == maxRating ]

    Which is slightly less intuitive because it forces us to iterate over the roles instead of over the movies.
    """

    __metaclass__ = OntologyClass

    # TODO: remove those variables which definition should be mandatory
    schema = ontology.Schema({})
    reverseLookup = {}
    valid = []
    unique = []
    order = []
    converters = {}

    # This variable works just like the 'schema' one, except that it only contains properties which have been defined
    # as a result of the reverseLookup names of other classes
    #_implicitSchema = {}

    def __init__(self, basenode = None, graph = None, allowIncomplete = False, **kwargs):
        log.debug('%s.__init__: basenode = %s, args = %s' % (self.__class__.__name__, basenode, kwargs))
        if graph is None and basenode is None:
            raise ValueError('You need to specify either a graph or a base node when instantiating a %s' % self.__class__.__name__)

        # just to make sure, while developing. This should probably be removed in a stable version
        if (#(graph is not None and not isinstance(graph, ObjectGraph)) or
            (basenode is not None and not (isinstance(basenode, ObjectNode) or
                                           isinstance(basenode, BaseObject)))):
                raise ValueError('Trying to build a BaseObject from a basenode, but you gave a \'%s\': %s' % (type(basenode).__name__, str(basenode)))

        created = False
        if basenode is None:
            # if no basenode is given, we need to create a new node
            self._node = graph.createNode(reverseLookup(kwargs, self.__class__),
                                          _classes = ontology.parentClasses(self.__class__))
            created = True

        else:
            basenode = getNode(basenode)

            # if basenode is already in this graph, no need to make a copy of it
            # if graph is None, we might just be making a new instance of a node, so it's in the same graph as well
            if graph is None or graph is basenode.graph():
                self._node = basenode
            else:
                # TODO: we should be able to construct directly from the other node
                self._node = graph.createNode(reverseLookup(basenode, self.__class__),
                                              _classes = basenode._classes)
                created = True

            # optimization: avoid revalidating the classes all the time when creating a BaseObject from a pre-existing node
            if kwargs:
                self.update(kwargs)

        # if we just created a node and the graph is static, we gave it its valid classes without actually checking...
        # if not a valid instance, remove it from the list of valid classes so that the next check will fail
        if created and not self._node.graph()._dynamic:
            if allowIncomplete and not self._node.hasValidProperties(self.__class__, self.__class__.valid.intersection(set(self._node.keys()))):
                self._node.removeClass(self.__class__)
            if not allowIncomplete and not self._node.isValidInstance(self.__class__):
                self._node.removeClass(self.__class__)


        # make sure that the new instance we're creating is actually a valid one
        # Note: the following comment shouldn't be necessary if the list of valid classes is always up-to-date
        #if not (self._node.isinstance(self.__class__) or
        #        (self._node._graph._dynamic and self._node.isValidInstance(self.__class__))):
        if not self._node.isinstance(self.__class__):
            # if we just created the node and it is invalid, we need to remove it
            if created:
                self._node.graph().deleteNode(self._node)

            raise TypeError("Cannot instantiate a valid instance of %s because:\n%s" %
                            (self.__class__.__name__, self._node.invalidProperties(self.__class__)))



    def __contains__(self, prop):
        return prop in self._node

    def get(self, name):
        try:
            return getattr(self, name)
        except:
            return None

    def __getattr__(self, name):
        result = getattr(self._node, name)

        # if the result is an ObjectNode, wrap it with the class it has been given in the class schema
        # if it was not in the class schema, simply returns an instance of BaseObject
        if isinstance(result, types.GeneratorType):
            resultClass = self.__class__.schema.get(name) or BaseObject
            return toresult([ resultClass(basenode = n) for n in result ])

        # FIXME: better test here (although if the graph is consistent (ie: always returns generators) it shouldn't be necessary)
        #elif isinstance(result, list) and isinstance(result[0], AbstractNode):
        #    resultClass = self.__class__.schema.get(name) or BaseObject
        #    return [ resultClass(basenode = node) for node in result ]

        else:
            return result


    def __setattr__(self, name, value):
        if name == '_node':
            object.__setattr__(self, name, value)
        else:
            self.set(name, value)

    def _applyMulti(self, func, name, value, validate):
        cls = self.__class__
        if name in cls.schema._implicit:
            raise ValueError("Implicit properties are read-only (%s.%s)" % (cls.__name__, name))

        # if mode == STRICT and name not in cls.schema:
        #     raise ValueError("Unknown property in the class schema: (%s.%s)" % (cls.__name__, name))

        # objects are statically-typed here; graphType == 'STATIC'
        # this also converts value to the correct type if an autoconverter was given in the class definition
        # and replaces BaseObjects with their underlying nodes.
        value = checkClass(name, value, cls.schema)

        # if we don't have a reverse lookup for this property, default to a reverse name of 'is%(Property)Of'
        reverseName = self.__class__.reverseLookup.get(name) or isOf(name)

        func(name, value, reverseName, validate)

    def set(self, name, value, validate = True):
        """Sets the given value to the named property."""
        self._applyMulti(self._node.set, name, value, validate)

    def append(self, name, value, validate = True):
        self._applyMulti(self._node.append, name, value, validate)

    def __eq__(self, other):
        # TODO: should allow comparing a BaseObject with an ObjectNode?
        if not isinstance(other, BaseObject): return False

        if self._node == other._node: return True

        # FIXME: this could lead to cycles or very long chained __eq__ calling on properties
        return self.explicitItems() == other.explicitItems()

    def __str__(self):
        return self._node.toString(cls = self.__class__, default = BaseObject).encode('utf-8')

    def __repr__(self):
        return self.__str__()

    def explicitItems(self):
        return [ x for x in self.items() if x[0] not in self.__class__.schema._implicit ]

    @classmethod
    def className(cls):
        return cls.__name__

    @classmethod
    def parentClass(cls):
        return cls.__mro__[1]

    def update(self, props):
        props = toNodes(props)
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
        return tuple(self.get(k) for k in self.__class__.unique)


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

