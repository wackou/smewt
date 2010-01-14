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

from objectgraph import ObjectGraph
from persistentobjectnode import PersistentObjectNode
import logging

log = logging.getLogger('smewt.datamodel.Neo4jObjectGraph')


class Neo4jObjectGraph(MemoryObjectGraph):
    """A Neo4jObjectGraph is an ObjectGraph where all data is persistent on disk.
    All attribute modifications are immediately synchronized on the data store.

    A Neo4jObjectGraph uses PersistentObjectNodes."""
    _objectNodeClass = PersistentObjectNode

    def __init__(self, dbpath):
        MemoryObjectGraph.__init__(self)
        neo.open(dbpath)

    def clear(self):
        """Delete all objects in this graph."""
        # FIXME
        for n in self._nodes:
            n._graph = None
        self._nodes.clear()

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        # FIXME
        return getNode(node) in self._nodes


    def nodes(self):
        # FIXME
        for node in self._nodes:
            yield node


    def removeDirectedEdge(self, node, name, otherNode):
        MemoryObjectGraph.removeDirectedEdge(self, node, name, otherNode)

        # TODO: how to do this in neo4j?

    def addDirectedEdge(self, node, name, otherNode):
        MemoryObjectGraph.addDirectedEdge(self, node, name, otherNode)

        # TODO: how to do this in neo4j?
