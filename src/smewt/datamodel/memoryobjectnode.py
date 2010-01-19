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
from utils import tolist, toresult, isLiteral, toIterator
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectNode')

class MemoryNode(BasicNode):

    def __init__(self, graph, props = []):
        print 'MemoryNode.__init__'
        graph._nodes.add(self)

        # NB: this should go before super().__init__() because we need self._props to exist
        #     before we can set attributes
        self._props = {}
        self._classes = set()
        super(MemoryNode, self).__init__(graph, props)


    def __eq__(self, other):
        return self is other

    def __hash__(self):
        # TODO: verify me
        return id(self)

    def addClass(self, cls):
        self._classes.add(cls)

    def removeClass(self, cls):
        self._classes.remove(cls)

    def clearClasses(self):
        self._classes = set()

    def classes(self):
        return self._classes

    def isinstance(self, cls):
        return cls in self._classes



    ### Acessing properties methods

    def getLiteral(self, name):
        # if name is not a literal, we need to throw an exception
        result = self._props[name]
        if isLiteral(result):
            return result
        raise AttributeError

    def getLink(self, name):
        # if name is not an edge, we need to throw an exception
        result = self._props[name]
        if not isLiteral(result):
            return toIterator(result)
        raise AttributeError

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



    def __setattr__(self, name, value):
        if name == '_props':
            object.__setattr__(self, name, value)
        else:
            super(MemoryNode, self).__setattr__(name, value)


    def setLiteral(self, name, value):
        self._props[name] = value

    def outgoingEdgeEndpoints(self, name = None):
        if name is not None:
            for ep in tolist(self._props[name]):
                yield ep
        else:
            print self._props
            print list(self.literalKeys())
            print list(self.edgeKeys())
            for prop, eps in self.edgeItems():
                print 'it', prop
                for ep in eps:
                    yield ep

    ### Container methods

    def literalKeys(self):
        return (k for k, v in self._props.items() if isLiteral(v))

    def literalValues(self):
        return (v for v in self._props.values() if isLiteral(v))

    def literalItems(self):
        return ((k, v) for k, v in self._props.items() if isLiteral(v))

    def edgeKeys(self):
        return (k for k, v in self._props.items() if not isLiteral(v))

    def edgeValues(self):
        return (toIterator(v) for v in self._props.values() if not isLiteral(v))

    def edgeItems(self):
        return ((k, toIterator(v)) for k, v in self._props.items() if not isLiteral(v))

    # the next ones are overriden for efficiency

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

# MemoryNode needs to come before ObjectNode, because we want it to be able to
# override ObjectNode's methods (for optimization, for instance)
class MemoryObjectNode(MemoryNode, ObjectNode):
    def __init__(self, graph, props = []):
        print 'MemoryObjectNode.__init__', props
        super(MemoryObjectNode, self).__init__(graph, props)
        # FIXME: this shouldn't be like that
        #MemoryNode.__init__(self, graph)
        #ObjectNode.__init__(self, props)
        pass
