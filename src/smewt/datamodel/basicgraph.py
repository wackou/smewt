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

log = logging.getLogger('smewt.datamodel.BasicGraph')


class Equal:
    # some constants
    OnIdentity = 1
    OnValue = 2
    OnValidValue = 3
    OnUniqueValue = 4



class BasicGraph(object):
    def clear(self):
        """Delete all nodes and links in this graph.
        Should be called by subclasses."""
        for n in self._nodes:
            n._graph = None

    def createNode(self, props):
        # FIXME: this might not work anymore (multiple inheritance)
        return self.__class__._objectNodeClass(self, props)

    def deleteNode(self, node):
        """Remove a given node.

        strategies for what to do with linked nodes should be configurable, ie:
        remove incoming/outgoing linked nodes as well, only remove link but do not
        touch linked nodes, etc..."""
        raise NotImplementedError

    def nodes(self):
        """Return an iterator that goes over all the nodes in the graph."""
        raise NotImplementedError

    def addDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        node.addDirectedEdge(name, otherNode)

    def removeDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        node.removeDirectedEdge(name, otherNode)

    def contains(self, node):
        """Return whether this graph contains the given node.

        multiple strategies can be used here for determing object equality, such as
        all properties equal, the primary subset of properties equal, etc... (those are defined
        by the ObjectNode)"""
        raise NotImplementedError

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        raise NotImplementedError


    def findNode(self, node, cmp = Equal.OnIdentity, excludeProperties = []):
        """Return a node in the graph that is equal to the given one using the specified comparison type.

        Return None if not found."""

        if cmp == Equal.OnIdentity:
            if node in self:
                log.info('%s already in graph %s (id)...' % (node, self))
                return node

        elif cmp == Equal.OnValue:
            for n in self._nodes:
                if node.sameProperties(n, exclude = excludeProperties):
                    log.info('%s already in graph %s (value)...' % (node, self))
                    return n
        else:
            raise NotImplementedError

        return None




class BasicNode(object):
    """This is the class one should inherit from when providing a specific implementation of a Node.

    You need only implement those methods which are necessary to be defined for a node that can have
    literal properties and named edges to other nodes in a directed graph.
    These signaled in this interface by raising NotImplementedError."""

    def __init__(self, graph, props = []):
        self._graph = graph
        self._classes = [] # TODO: should go in the mem implementation

        # contains reverseName, should go into ObjectNode
        for prop, value, reverseName in props:
            self.set(prop, value, reverseName, validate = False)

        self.updateValidClasses()


    def __eq__(self, other):
        # This should implement identity of nodes, not properties equality (this should be done
        # in the BaseObject instance)
        raise NotImplementedError

    ### Methods needed for storing the nodes ontology (caching)
    ### Note: this could be implemented only using literal values, but it is left
    ###       as part of the API as this is something which is used a lot and benefits
    ###       a lot from being optimized, which can be more easily done in the implementation

    def addClass(self, cls):
        """Add the given class to the list of valid classes for this node."""
        raise NotImplementedError

    def removeClass(self, cls):
        """Remove the given class from the list of valid classes for this node."""
        raise NotImplementedError

    def isinstance(self, cls):
        raise NotImplementedError

    def nodesFromClass(self, cls):
        """Return all the nodes of a given class."""
        raise NotImplementedError



    def getLiteral(self, name):
        raise NotImplementedError

    def setLiteral(self, name, value):
        """Need to be implemented by implementation subclass.
        Can assume that literal is always one of the valid literal types."""
        raise NotImplementedError

    def literalKeys(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def literalValues(self):
        raise NotImplementedError

    def literalItems(self):
        raise NotImplementedError


    def addDirectedEdge(self, name, otherNode):
        raise NotImplementedError

    def removeDirectedEdge(self, name, otherNode):
        raise NotImplementedError

    def outgoingEdgeEndpoints(self, name = None):
        """Return all the nodes which this node points to with the given edge type.
        If name is None, return all outgoing edge points."""
        raise NotImplementedError

    def edgeKeys(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def edgeValues(self):
        # TODO: should return an iterator of (iterator on BasicNodes)
        raise NotImplementedError

    def edgeItems(self):
        raise NotImplementedError

    def sameProperties(self, other, exclude = []):
        # NB: sameValidProperties and sameUniqueProperties should be defined in BaseObject
        # TODO: this can surely be optimized
        for name, value in other.items():
            if name in exclude:
                continue
            if self.get(name) != value:
                return False

        return True


