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
from basicgraph import BasicNode
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectNode')

class MemoryNode(BasicNode):

    def __init__(self, graph, props = []):
        graph._nodes.add(self)

        # NB: this should go before super().__init__() because we need self._props to exist
        #     before we can set attributes
        self._props = {}
        BasicNode.__init__(self, graph, props)


    def __eq__(self, other):
        return self is other

    def __hash__(self):
        # TODO: verify me
        return id(self)

    ### Acessing properties methods

    def getLiteral(self, name):
        return getattr(self, name)

    def getLink(self, name):
        return getattr(self, name)

    def removeDirectedEdge(self, name, otherNode):
        # otherNode should always be a valid node
        nodeList = tolist(self._props.get(name))
        nodeList.remove(otherNode)
        self._props[name] = toresult(nodeList)

        # TODO: we should have this, right?
        if list(node._props[name]) == []:
            del node._props[name]

    def addDirectedEdge(self, name, otherNode):
        # otherNode should always be a valid node
        nodeList = tolist(self._props.get(name))
        nodeList.append(otherNode)
        self._props[name] = toresult(nodeList)



    def __getattr__(self, name):
        try:
            return self._props[name]
        except KeyError:
            raise AttributeError, name


    def __setattr__(self, name, value):
        if name == '_props':
            object.__setattr__(self, name, value)
        else:
            ObjectNode.__setattr__(self, name, value)


    def setLiteral(self, name, value):
        self._props[name] = value


    ### Container methods

    def keys(self):
        return self._props.keys()

    def values(self):
        return self._props.values()

    def items(self):
        return self._props.items()


    ### manipulation methods

    '''
    def updateNew(self, other):
        for name, value in other._props.items():
            if name not in self._props:
                self._props[name] = value
    '''

class MemoryObjectNode(ObjectNode, MemoryNode):
    pass
