#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@gmail.com>
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

class Graph:
    '''This class represents an acyclic directed graph of nodes, where the nodes can either be
    Media or Metadata objects. The links are direct references from one node to the other, and
    are not represented explicitly.

    One can filter by type, property or any combination of those.
    '''

    def findOrCreate(self, type = None, **kwargs):
        '''This method returns the first object in this graph which has the specified type and
        properties which match the given keyword args dictionary.
        If no match is found, it creates a new object with the keyword args, inserts it in the
        graph, and returns it.

        example: g.findOrCreate(Series, title = 'Arrested Development')'''
        pass

    def findAll(self, type = None, **kwargs):
        '''This method returns all the objects in this graph which have the specified type and
        properties which match the given keyword args dictionary. If no keyword args are specified,
        it matches all the object of the given type.
        If no match is found, it returns an empty list.

        example: g.findAll(Episodes)'''
        pass

    def __iadd__(self, obj):
        '''Adds the object to the current graph. It can be either a single Node, a list of nodes,
        or another Graph.
        In case there are duplicates nodes (ie: they have the same unique properties), they will
        be merged to use a single Node.'''
        pass
