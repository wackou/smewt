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

log = logging.getLogger('smewt.datamodel.AbstractDirectedGraph')


class Equal:
    # some constants
    OnIdentity = 1
    OnValue = 2
    OnValidValue = 3
    OnUniqueValue = 4



class AbstractDirectedGraph(object):
    """This class describes a basic directed graph, with the addition that the nodes have a special
    property "classes" which describe which class an node can "morph" into. This mechanism could be
    built as another basic node property, but it is not for performance reasons.

    The AbstractDirectedGraph class is the basic interface one needs to implement for providing
    a backend storage of the data. It is complementary to the AbstractNode interface.

    You only need to provide the implementation for this interface, and then an ObjectGraph can
    be automatically built upon it.

    The methods you need to implement fall into the following categories:
     - create / delete node(s)
     - get all nodes / only nodes from a given class
     - check whether a node lives in a given graph
     - find a node given a list of matching properties

    """
    def clear(self):
        """Delete all nodes and links in this graph.

        NB: This method should be called by subclasses that reimplement or extend it."""
        for n in self._nodes:
            n._graph = None

    def createNode(self, props = []):
         raise NotImplementedError

    def deleteNode(self, node):
        """Remove a given node.

        strategies for what to do with linked nodes should be configurable, ie:
        remove incoming/outgoing linked nodes as well, only remove link but do not
        touch linked nodes, etc..."""
        raise NotImplementedError

    def nodes(self):
        """Return an iterator on all the nodes in the graph."""
        raise NotImplementedError

    def nodesFromClass(self, cls):
        """Return an iterator on the nodes of a given class."""
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
        # TODO: remove this, as it should only be implemented in the ObjectGraph
        raise NotImplementedError


    def findNode(self, node, cmp = Equal.OnIdentity, excludeProperties = []):
        """Return a node in the graph that is equal to the given one using the specified comparison type.

        Return None if not found."""

        if cmp == Equal.OnIdentity:
            if self.contains(node):
                log.info('%s already in graph %s (id)...' % (node, self))
                return node

        elif cmp == Equal.OnValue:
            for n in self.nodes():
                if node.sameProperties(n, exclude = excludeProperties):
                    log.info('%s already in graph %s (value)...' % (node, self))
                    return n

        else:
            raise NotImplementedError

        return None


