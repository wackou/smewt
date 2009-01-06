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

from PyQt4.QtCore import QObject, SIGNAL
from mediaobject import Media, Metadata
import yaml, logging

class Graph(QObject):
    '''This class represents an acyclic directed graph of nodes, where the nodes can either be
    Media or Metadata objects. The links are direct references from one node to the other, and
    are not represented explicitly.

    One can filter by type, property or any combination of those.
    '''

    def __init__(self):
        super(Graph, self).__init__()
        self.nodes = set()

    def __str__(self):
        return 'Graph: { %s }' % self.nodes

    def findOrCreate(self, type, **kwargs):
        '''This method returns the first object in this graph which has the specified type and
        properties which match the given keyword args dictionary.
        If no match is found, it creates a new object with the keyword args, inserts it in the
        graph, and returns it.

        example: g.findOrCreate(Series, title = 'Arrested Development')'''
        result = []
        # FIXME: also filter by kwargs
        for node in self.nodes:
            if isinstance(node, type):
                return node

        node = type(kwargs)
        self += node
        return node

    def findAll(self, type, **kwargs):
        '''This method returns all the objects in this graph which have the specified type and
        properties which match the given keyword args dictionary. If no keyword args are specified,
        it matches all the object of the given type.
        If no match is found, it returns an empty list.

        example: g.findAll(Episodes)'''
        result = []
        # FIXME: also filter by kwargs
        for node in self.nodes:
            if isinstance(node, type):
                result.append(node)
        return result

    def __iadd__(self, obj):
        '''Adds the object to the current graph. It can be either a single Node, a list of nodes,
        or another Graph.
        In case there are duplicates nodes (ie: they have the same unique properties), they will
        be merged to use a single Node.'''
        # FIXME: detect duplicates

        if isinstance(obj, list):
            for o in obj:
                self.addNode(o)
        elif isinstance(obj, Graph):
            for o in obj.nodes:
                self.addNode(o)
        else:
            self.addNode(obj)

        self.emit(SIGNAL('updated'))
        return self

    def addNode(self, obj):
        '''adds a single node and its links recursively.'''
        # add object itself...
        self.nodes.add(obj)

        # ...and follow links if any
        if isinstance(obj, Media):
            self.addNode(obj.metadata)

        elif isinstance(obj, Metadata):
            for prop, type in obj.schema.items():
                if isinstance(type, Metadata):
                    self.addNode(obj[prop])

    def load(self, filename):
        try:
            f = open(filename)
        except:
            # if file is not found, just go on with an empty collection
            logging.warning('Collection "%s" does not exist' % filename)
            self.nodes = set()
            return

        self.nodes = yaml.load(f.read())

    def save(self, filename):
        open(filename, 'w').write(yaml.dump(self.nodes))
