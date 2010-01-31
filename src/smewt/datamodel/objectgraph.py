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
from abstractdirectedgraph import AbstractDirectedGraph
from abstractnode import AbstractNode
from baseobject import BaseObject, getNode
from utils import reverseLookup, toresult
import types
import ontology
import logging

log = logging.getLogger('smewt.datamodel.ObjectGraph')


class Equal:
    # some constants
    OnIdentity = 1
    OnValue = 2
    OnValidValue = 3
    OnUniqueValue = 4



def wrapNode(node, nodeClass = None):
    if nodeClass is None:
        nodeClass = BaseObject
    return nodeClass(basenode = node)

def unwrapNode(node):
    nodeClass = node.__class__ if isinstance(node, BaseObject) else None
    node = getNode(node)

    return node, nodeClass



class ObjectGraph(AbstractDirectedGraph):
    """An ObjectGraph is an undirected graph of ObjectNodes.
    An ObjectNode "looks like" an object, with a class type and any number of properties/attributes,
    which can be either literal values or other objects in the graph. These properties are accessed
    using dotted attribute notation.

    The ObjectGraph edges (links) are a bit special in that they are undirected but have a different
    name depending on the direction in which they are followed, e.g.: if you have two nodes, one
    which represent a series, and another one which represent an episode, the link will be named
    "series" when going from the episode to the series, but will be named "episodes" when going from
    the series to the episode.

    When setting a link in the graph, you should define a name for the reverse name of the link, but if
    you don't a default name of "is(%Property)Of" will be given to it.
    For instance, if we have movie.director == personX, we should also have
    personX.isDirectorOf == movie (actually "movie in personX.isDirectorOf").

    The ObjectGraph class provides ways of querying objects in it using type information,
    properties matching filters, or just plain lambda functions that returns whether a node
    is acceptable or not.

    An ObjectGraph can be thought of as a context in which objects live.

    Even though the dotted attribute access makes this less visible, the links between ObjectNodes
    are first-class citizens also, and can themselves have attributes, such as confidence, etc...
    """

    # this should be set to the used ObjectNode class (ie: MemoryObjectNode or Neo4jObjectNode)
    # in the corresponding derived ObjectGraph class
    _objectNodeClass = type(None)

    def __init__(self, dynamic = False):
        """Creates an ObjectGraph.

        - if dynamic = True, we have static inheritance (valid classes need to be set explicitly)
        - if dynamic = False, we have dynamic type classes (valid classes are automatically updated if the object has the correct properties)
        """
        ontology.registerGraph(self)
        self._dynamic = dynamic

    def revalidateObjects(self):
        if not self._dynamic:
            return

        log.info('revalidating objects in graph %s' % self)
        for node in self.nodes():
            node.updateValidClasses()

    def __getattr__(self, name):
        # if attr is not found and starts with an upper case letter, it might be the name
        # of one of the registered classes. In that case, return a function that would instantiate
        # such an object in this graph
        if name[0].isupper() and name in ontology.classNames():
            def inst(basenode = None, **kwargs):
                return ontology.getClass(name)(basenode = basenode, graph = self, **kwargs)

            return inst

        raise AttributeError

    def __contains__(self, node):
        """Return whether this graph contains the given node  or object (identity)."""
        return self.contains(getNode(node))


    def addLink(self, node, name, otherNode, reverseName):
        # otherNode should always be a valid node
        self.addDirectedEdge(node, name, otherNode)
        self.addDirectedEdge(otherNode, reverseName, node)

    def removeLink(self, node, name, otherNode, reverseName):
        # otherNode should always be a valid node
        self.removeDirectedEdge(node, name, otherNode)
        self.removeDirectedEdge(otherNode, reverseName, node)


    def addNode(self, node, recurse = Equal.OnIdentity, excludedDeps = []):
        return self.addObject(BaseObject(node), recurse, excludedDeps)

    def addObject(self, node, recurse = Equal.OnIdentity, excludedDeps = []):
        """Add an object and its underlying node and its links recursively into the graph.

        If some dependencies of the node are already in the graph, we should not add
        new instances of them but use the ones already there (ie: merge links).

        This strategy should be configurable, and offer at least the following choices:
          - recurse = OnIdentity   : do not add the dependency only if the exact same node is already there
          - recurse = OnValue      : do not add the dependency only if there is already a node with the exact same properties
          - recurse = OnValidValue : do not add the dependency only if there is already a node with the same valid properties
          - recurse = OnUnique     : do not add the dependency only if there is already a node with the same unique properties
        """
        log.debug('Adding to graph: %s - node: %s' % (self, node))
        node, nodeClass = unwrapNode(node)

        if nodeClass is None:
            raise TypeError("Can only add BaseObjects to a graph at the moment...")

        # first make sure the node's not already in the graph, using the requested equality comparison
        # TODO: if node is already there, we need to decide what to do with the additional information we have
        #       in the added node dependencies: update missing properties, update all properties (even if already present),
        #       update non-valid properties, ignore new data, etc...
        excludedProperties = nodeClass.schema._implicit if nodeClass is not None else []
        log.debug('exclude properties: %s' % excludedProperties)

        gnode = self.findNode(node, recurse, excludedProperties)
        if gnode is not None:
            return wrapNode(gnode, nodeClass)

        # if node isn't already in graph, we need to make a copy of it that lives in this graph

        # first import any other node this node might depend on
        newprops = []
        for prop, value, reverseName in reverseLookup(node, nodeClass):
            #if (isinstance(value, AbstractNode) or
            #    (isinstance(value, list) and isinstance(value[0], AbstractNode))):
            if isinstance(value, types.GeneratorType):
                # use only the explicit properties here
                if prop not in excludedProperties and value not in excludedDeps:
                    importedNodes = []
                    for v in value:
                        log.debug('Importing dependency %s: %s' % (prop, v))
                        importedNodes.append(self.addObject(wrapNode(v, nodeClass.schema.get(prop)),
                                                            recurse,
                                                            excludedDeps = excludedDeps + [node])._node)
                    newprops.append((prop, importedNodes, reverseName))
            else:
                newprops.append((prop, value, reverseName))

        # actually create the node
        result = self.createNode(newprops, _classes = node._classes)

        return wrapNode(result, nodeClass)


    def __iadd__(self, node):
        """Should allow node, but also list of nodes, graph, ..."""
        if isinstance(node, list):
            for n in node:
                self.addObject(n)
        else:
            self.addObject(node)

        return self


    ### Search methods

    def findAll(self, type = None, validNode = lambda x: True, **kwargs):
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
          g.findall(Movie, lambda m: m.releaseYear > 2000)
          g.findAll(Person, role_movie_title = 'The Dark Knight')
          g.findAll(Character, isCharacterOf_movie_title = 'Fear and loathing.*', regexp = True)
        """
        return list(self._findAll(type, validNode, **kwargs))


    def _findAll(self, type = None, validNode = lambda x: True, **kwargs):
        """Implementation of findAll that returns a generator."""
        for node in self.nodesFromClass(type) if type else self.nodes():
            # TODO: should this go before or after the properties checking? Which is faster in general?
            if not validNode(node):
                continue

            valid = True
            for prop, value in kwargs.items():
                try:
                    # FIXME: this doesn't work with lists of objects
                    if isinstance(value, BaseObject):
                        value = value._node

                    if node.getChainedProperties(prop.split('_')) != value:
                        valid = False
                        break
                except AttributeError:
                    valid = False
                    break

            if not valid:
                continue

            if type:
                yield type(node)
            else:
                yield node


    def findOne(self, type = None, validNode = lambda x: True, **kwargs):
        """Returns a single result. see findAll for description.
        Raises an exception of no result was found."""
        # NB: as _findAll is a generator, this should be fairly optimized
        result = self._findAll(type, validNode, **kwargs)
        try:
            return result.next()
        except StopIteration:
            raise ValueError('Could not find given %s with props %s' % (type.__name__, kwargs))

    def findOrCreate(self, type, **kwargs):
        '''This method returns the first object in this graph which has the specified type and
        properties which match the given keyword args dictionary.
        If no match is found, it creates a new object with the keyword args, inserts it in the
        graph, and returns it.

        example: g.findOrCreate(Series, title = 'Arrested Development')'''
        try:
            return self.findOne(type, **kwargs)
        except ValueError:
            return type(graph = self, **kwargs)

