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
from basicgraph import BasicGraph
from memoryobjectnode import MemoryObjectNode
from baseobject import BaseObject, getNode
import ontology
from objectgraph import ObjectGraph
from utils import tolist, toresult
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectGraph')


class MemoryGraph(BasicGraph):
    _objectNodeClass = MemoryObjectNode

    def __init__(self):
        BasicGraph.__init__(self)
        self._nodes = set()

    def clear(self):
        """Delete all objects in this graph."""
        ObjectGraph.clear()
        self._nodes.clear()

    def deleteNode(self, node):
        raise NotImplementedError


    def nodes(self):
        for node in self._nodes:
            yield node

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        return node in self._nodes


class MemoryObjectGraph(MemoryGraph, ObjectGraph):
    pass
