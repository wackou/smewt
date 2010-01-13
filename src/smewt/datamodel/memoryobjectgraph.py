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
from memoryobjectnode import MemoryObjectNode
from baseobject import BaseObject, getNode
import ontology
from objectgraph import ObjectGraph
from utils import tolist, toresult
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectGraph')


class MemoryObjectGraph(ObjectGraph):
    _objectNodeClass = MemoryObjectNode

    def __init__(self):
        ObjectGraph.__init__(self)
        self._nodes = set()

    def clear(self):
        """Delete all objects in this graph."""
        for n in self._nodes:
            n._graph = None
        self._nodes.clear()

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        return getNode(node) in self._nodes


    def nodes(self):
        for node in self._nodes:
            yield node

    def removeLink(self, node, name, otherNode, reverseName):
        self.removeDirectedEdge(node, name, otherNode)
        self.removeDirectedEdge(otherNode, reverseName, node)

    def addLink(self, node, name, otherNode, reverseName):
        # otherNode should always be a valid node
        self.addDirectedEdge(node, name, otherNode)
        self.addDirectedEdge(otherNode, reverseName, node)

    def removeDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        nodeList = tolist(node._props.get(name))
        nodeList.remove(otherNode)
        node._props[name] = toresult(nodeList)

        # TODO: ? if node._props[name] == []: del node._props[name]

    def addDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        nodeList = tolist(node._props.get(name))
        nodeList.append(otherNode)
        node._props[name] = toresult(nodeList)

