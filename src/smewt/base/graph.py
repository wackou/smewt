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
from smewtexception import SmewtException
import logging, cPickle

log = logging.getLogger('smewt.base.graph')

class Graph(QObject):
    '''This class represents an acyclic directed graph of nodes, where the nodes can either be
    Media or Metadata objects. The links are direct references from one node to the other, and
    are not represented explicitly.

    One can filter by type, property or any combination of those.
    '''

    def __init__(self):
        super(Graph, self).__init__()
        self.nodes = set()

    def clear(self):
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

    def findAll(self, select = lambda x: True, type = None, **kwargs):
        '''This method returns a list of the objects in this graph which pass the select filter and are
        instances of the specified type. It will also only keep those objects that have properties
        which match the given keyword args dictionary.

        When using both the select function and the type argument, it is useful to know that the
        type is checked first, so that the select function can safely assume that only objects of
        the correct type are given to it.

        If no match is found, it returns an empty list.

        example:
          g.findAll(type = Movie)
          g.findAll(lambda x: x['season'] = 2, type = Episode)
          '''
        if type:
            validNode = select
            select = lambda x: isinstance(x, type) and validNode(x)

        result = []
        for node in self.nodes:
            if not select(node):
                continue

            valid = True
            for prop, value in kwargs.items():
                if node[prop] != value:
                    valid = False
                    break

            if not valid:
                continue

            result.append(node)

        return result

    def findOne(self, select = lambda x: True, type = None, **kwargs):
        '''This method returns the first object in this graph which passes the select filter and is
        an instance of the specified type. It will also discard those objects that have properties
        which don't match the given keyword args dictionary.

        When using both the select function and the type argument, it is useful to know that the
        type is checked first, so that the select function can safely assume that only objects of
        the correct type are given to it.

        If no match is found, it raises a SmewtException.

        example: g.findOne(type = Movie, title = 'Fear and Loathing in Las Vegas')'''
        if type:
            validNode = select
            select = lambda x: isinstance(x, type) and validNode(x)

        result = []
        for node in self.nodes:
            if not select(node):
                continue

            valid = True
            for prop, value in kwargs.items():
                if node[prop] != value:
                    valid = False
                    break

            if not valid:
                continue

            return node

        raise SmewtException('Graph: could not find %s matching the following criteria: %s' % (type.typename, str(kwargs)))

    def findExact(self, md):
        '''Returns the exact object in that graph which corresponds to the given Metadata object.'''
        result = None
        for obj in self.nodes:
            if md == obj:
                return obj

        raise SmewtException('Graph: could not find given object inside graph!')

    def update(self, md, prop, value):
        '''Updates a property part of the unique-defining ones from an object already in the collection.
        This is usually not possible directly because the object is immutable.'''
        # NB: we won't have to update any refs because this is still the same object,
        #     we're not making any copy
        obj = self.findExact(md)

        # first remove it from the graph...
        self.nodes.remove(obj)

        # ...update the value...
        obj.mutable = True
        obj[prop] = value
        obj.mutable = False

        # ...and insert object back in the graph
        self.nodes.add(obj)

    def __iadd__(self, obj):
        '''Adds the object to the current graph. It can be either a single Node, a list of nodes,
        or another Graph.
        In case there are duplicates nodes (ie: they have the same unique properties), they will
        be merged to use a single Node.'''
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
        # FIXME: when reimporting, subtitles do not get merged correctly but added...
        if obj is None:
            return

        # if node is already in there, merge the info we don't have yet
        if obj in self.nodes:
            if isinstance(obj, Metadata):
                for elem in self.nodes:
                    if elem == obj:
                        elem.mergeNew(obj)

            return

        # first, follow links if any...
        if isinstance(obj, Media):
            self += obj.metadata

        elif isinstance(obj, Metadata):
            for prop, type in obj.schema.items():
                if issubclass(type, Metadata):
                    # check whether it is already in the set and update ref accordingly, add it otherwise
                    value = obj[prop]
                    found = None # need to keep it a separate var to add later cause we can't do it while iterating the set
                    for elem in self.nodes:
                        # we need to update the ref only if there is an equivalent object in there which is NOT the same
                        # in that case, we also need to make a copy of the object otherwise we might change the ref from
                        # an outside object which we shouldn't be touching
                        if elem == value:
                            found = elem
                            if elem is not value:
                                obj = obj.__class__(obj)
                                obj[prop] = elem
                                # also merge additional info we might have
                                # FIXME: this needs to be recursive
                                obj[prop].mergeNew(value)
                            break
                    if not found:
                        self.addNode(value)

            # object needs to be immutable because we need its __hash__ method to be correct from now on
            obj.mutable = False

        # ...then add object itself once its refs have been correctly updated
        self.nodes.add(obj)


    def load(self, filename):
        try:
            f = open(filename)
        except:
            # if file is not found, just go on with an empty collection
            log.warning('Collection "%s" does not exist' % filename)
            self.nodes = set()
            return

        self.nodes = cPickle.load(f)

    def save(self, filename):
        cPickle.dump(self.nodes, open(filename, 'w'))

