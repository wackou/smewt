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
from baseobject import BaseObject, getNode
import ontology
import logging

log = logging.getLogger('smewt.datamodel.ObjectGraph')

# TODO: make these functionas available everywhere
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


class Recurse:
    # some constants
    OnIdentity = 1
    OnValue = 2
    OnValidValue = 3
    OnUniqueValue = 4


def unwrapNode(node):
    nodeClass = node.__class__ if isinstance(node, BaseObject) else None
    node = getNode(node)

    return node, nodeClass


class ObjectGraph(object):
    """An ObjectGraph is a directed graph of nodes in which each node is actually an object,
    with a class type and any number of properties/attributes, which can be either literal
    values or other objects in the graph.

    The links in the graph are actually the properties of objects which are other objects
    in the ObjectGraph instead of being literal values.

    Those objects class shall be the python one, even though they need to define a instance_of()
    method, and their properties should be available using the dotted notation, ie:
    movie.director.first_name = 'kubrick'.

    Reverse attributes should be made automatically available using the "is_*_of" pattern.
    For instance, if we have movie.director == personX, we should also have
    personX.is_director_or == movie (or at least "movie in personX.is_director_or").
    This reverse-attribute lookup can only work when the Node has first been inserted into
    a graph.

    The ObjectGraph class provides ways of querying objects in it using type information,
    properties matching filters, or just plain lambda functions that returns whether a node
    is acceptable or not.

    An ObjectGraph can be thought of as a context in which objects live.

    Even though the dotted attribute access makes this less visible, the links between ObjectNodes
    are first-class citizens also, and can themselves have attributes, such as confidence, etc...
    """

    # this should be set to the used ObjectNode class (ie: ObjectNode or PersistentObjectNode)
    _objectNodeClass = type(None)

    def __init__(self):
        self._nodes = set()
        OntologyManager.registerGraph(self)

    def clear(self):
        """Delete all objects in this graph."""
        for n in self._nodes:
            n._graph = None
        self._nodes.clear()

    def revalidateObjects(self):
        for node in self._nodes:
            node.updateValidClasses()

    def __getattr__(self, name):
        # if attr is not found and starts with an upper case letter, it might be the name
        # of one of the registered classes. In that case, return a function that would instantiate
        # such an object in this graph
        if name[0].isupper() and name in ontology.classNames():
            def inst(basenode = None, **kwargs):
                return ontology.getClass(name)(self, basenode, **kwargs)

            return inst

        raise AttributeError


    def contains(self, node):
        """Return whether this graph contains the given node.

        multiple strategies can be used here for determing object equality, such as
        all properties equal, the primary subset of properties equal, etc... (those are defined
        by the ObjectNode)"""
        raise NotImplementedError

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        raise NotImplementedError

    # TODO: implement iterator / generator interface (ie: for node in graph: do...)

    def createNode(self, **kwargs):
        return self.__class__._objectNodeClass(self, **kwargs)


    def wrapNode(self, node, nodeClass = None):
        if nodeClass is not None:
            return nodeClass(self, basenode = node)

        return node


    def importNodeDependencies(self, node, recurse):
        """Import all the other nodes this node depends on, and update this node's links."""
        for name, value in node.items():
            if isinstance(value, ObjectNode) or isinstance(value, BaseObject):
                print 'also adding node', value
                setattr(node, name, self.addNode(value, recurse))


    def addNode(self, node, recurse = Recurse.OnIdentity):
        """Add a single node and its links recursively into the graph.

        If some dependencies of the node are already in the graph, we should not add
        new instances of them but use the ones already there (ie: merge links).

        This strategy should be configurable, and offer at least the following choices:
          - recurse = OnIdentity   : do not add the dependency only if the exact same node is already there
          - recurse = OnValue      : do not add the dependency only if there is already a node with the exact same properties
          - recurse = OnValidValue : do not add the dependency only if there is already a node with the same valid properties
          - recurse = OnUnique     : do not add the dependency only if there is already a node with the same unique properties
        """

        node, nodeClass = unwrapNode(node)

        # first make sure the node's not already in the graph, using the requested equality comparison
        if recurse == Recurse.OnIdentity:
            if node in self:
                print 'already in graph (id)...'
                return self.wrapNode(node, nodeClass)

        elif recurse == Recurse.OnValue:
            for n in self._nodes:
                if node.sameProperties(n):
                    print 'already in graph (value)...'
                    return self.wrapNode(n, nodeClass)
        else:
            raise NotImplementedError

        # if node isn't already in graph, we need to make a copy of it that lives in this graph
        result = self.createNode(**dict(node.items()))

        # first add any node this node might depend on
        self.importNodeDependencies(result, recurse)

        # now add node
        self._addNode(result)

        # NB: possible optimization: we know the node should be valid, no need to recreate an instance
        #     from scratch and re-validate its properties
        return self.wrapNode(result, nodeClass)


    def __iadd__(self, node):
        """Should allow node, but also list of nodes, graph, ..."""
        if isinstance(node, list):
            for n in node:
                self.addNode(n)
        else:
            self.addNode(node)

        return self

    def removeNode(self, node):
        """Remove a given node.

        strategies for what to do with linked nodes should be configurable, ie:
        remove incoming/outgoing linked nodes as well, only remove link but do not
        touch linked nodes, etc..."""
        raise NotImplementedError

    ### Search methods

    def reverseLookup(self, node, propname):
        """Return all the nodes in the graph which have a property which name is propname
        and which value is the given node."""
        # FIXME: this is completely not optimized...
        # FIXME: make sure this is == we want here, and not some other equality type
        return toresult([ n for n in self._nodes if n.get(propname) == node ])


    def findAll(self, type = None, cond = lambda x: True, **kwargs):
        """This method returns a list of the objects of the given type in this graph for which
        the cond function returns True (or sth that evaluates to True).
        It will also only keep those objects that have properties which match the given keyword
        args dictionary.

        When using both the cond function and the type argument, it is useful to know that the
        type is checked first, so that the cond function can safely assume that only objects of
        the correct type are given to it.

        When using keyword args for filtering, you can chain properties using '_' between them.
        it should be configurable whether property value matching should be case-insensitive or
        use regexps in the case of strings.

        If no match is found, it returns an empty list.

        examples:
          g.findAll(type = Movie)
          g.findAll(Episode, lambda x: x.season = 2)
          g.findall(Movie, lambda m: m.release_year > 2000)
          g.findAll(Person, role_movie_title = 'The Dark Knight')
          g.findAll(Character, isCharacterOf_movie_title = 'Fear and loathing.*', regexp = True)
        """
        # TODO: not really optimized, we could index on class type, etc...
        result = []

        if type:
            validNode = cond
            cond = lambda x: x.isinstance(type) and validNode(x)

        for node in self._nodes:
            if not cond(node):
                continue

            valid = True
            for prop, value in kwargs.items():
                if node.get(prop) != value:
                    valid = False
                    break

            if not valid:
                continue

            result.append(node)

        return result


    def findOne(self, type = None, cond = lambda x: True, **kwargs):
        """Returns 1 result. see findAll for description."""
        pass

    def findOrCreate(self, type, **kwargs):
        '''This method returns the first object in this graph which has the specified type and
        properties which match the given keyword args dictionary.
        If no match is found, it creates a new object with the keyword args, inserts it in the
        graph, and returns it.

        example: g.findOrCreate(Series, title = 'Arrested Development')'''
        raise NotImplementedError
