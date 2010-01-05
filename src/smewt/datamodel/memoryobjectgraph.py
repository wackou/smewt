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
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectGraph')


class MemoryObjectGraph(ObjectGraph):

    def __init__(self):
        self._nodes = set()
        self._objectNodeImpl = MemoryObjectNode

    def clear(self):
        """Delete all objects in this graph."""
        for n in self._nodes:
            n._graph = None # TODO: really necessary?
        self._nodes.clear()

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        return getNode(node) in self._nodes

    # TODO: implement iterator / generator interface (ie: for node in graph: do...)


    def _addNode(self, node):
        self._nodes.add(node)

    def __iadd__(self, node):
        """Should allow node, but also list of nodes, ..."""
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
        """examples:
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
