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
            n._graph = None # TODO: really necessary?
        self._nodes.clear()

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        return getNode(node) in self._nodes


    def nodes(self):
        for node in self._nodes:
            yield node

    def _addNode(self, node):
        self._nodes.add(node)

    '''
    def setLink(self, node, name, otherNode, otherName):
        # FIXME: need to do the reverse as well
        #node._props[name] = otherNode
        # FIXME: when we don't do remove, some tests fail. This might hide a potential bug.
        self.removeDirectedEdge(node, None, name)
        self.addDirectedEdge(node, otherNode, name)

        self.addDirectedEdge(otherNode, node, otherName)

    def setLink2(self, node, name, otherNode, otherName):
        # first remove the old link(s)
        for n in tolist(node.get(name)):
            self.removeLink(node, name, n, otherName)
        # then add the new link
        self.addLink(node, name, otherNode, otherName)
    '''

    def removeLink(self, node, name, otherNode, reverseName):
        print 'removeLink', node, name, otherNode, reverseName
        self.removeDirectedEdge(node, name, otherNode)
        self.removeDirectedEdge(otherNode, reverseName, node)

    def addLink(self, node, name, otherNode, reverseName):
        # otherNode should always be a valid node
        print 'addLink', node, name, otherNode, reverseName
        self.addDirectedEdge(node, name, otherNode)
        self.addDirectedEdge(otherNode, reverseName, node)

    def removeDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        # FIXME: for lists
        #if otherNode is None:
        #    node._props[name] = []
        #else:
        #    node._props[name].remove(otherNode)

        print 'remove edge', node, name, otherNode
        nodeList = tolist(node._props.get(name))
        print 'from', nodeList
        nodeList.remove(otherNode)
        node._props[name] = toresult(nodeList)

        # if node._props[name] == []: del node._props[name]

    def addDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        print 'add edge', node, name, otherNode
        nodeList = tolist(node._props.get(name))
        nodeList.append(otherNode)
        node._props[name] = toresult(nodeList)


    ### Search methods

    def reverseLookup(self, node, propname):
        """Return all the nodes in the graph which have a property which name is propname
        and which value is the given node.
        This always returns a list of nodes."""
        # FIXME: this is completely not optimized...
        return [ n for n in self._nodes if n.get(propname) == node ]

