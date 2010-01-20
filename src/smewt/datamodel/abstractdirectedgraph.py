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
    def clear(self):
        """Delete all nodes and links in this graph.
        Should be called by subclasses."""
        for n in self._nodes:
            n._graph = None

    def createNode(self, props = []):
        # FIXME: this might not work anymore (multiple inheritance)
        return self.__class__._objectNodeClass(self, props)

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


