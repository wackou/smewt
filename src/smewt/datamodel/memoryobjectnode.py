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

from abstractnode import AbstractNode
from objectnode import ObjectNode
from utils import tolist, toresult, isLiteral, toIterator
import ontology
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectNode')

class MemoryNode(AbstractNode):

    def __init__(self, graph, props = [], _classes = set()):
        # NB: this should go before super().__init__() because we need self._props and
        #     self._classes to exist before we can set attributes
        self._props = {}
        self._classes = set(_classes)
        super(MemoryNode, self).__init__(graph, props)

        log.debug('MemoryNode.__init__: classes = %s' % list(self._classes))
        graph._nodes.add(self)


    def __eq__(self, other):
        return self is other

    def __hash__(self):
        # TODO: verify me
        return id(self)

    def __setattr__(self, name, value):
        if name in [ '_props', '_classes' ]:
            object.__setattr__(self, name, value)
        else:
            super(MemoryNode, self).__setattr__(name, value)


    ### Ontology methods

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



    ### Accessing literal properties

    def getLiteral(self, name):
        # if name is not a literal, we need to throw an exception
        result = self._props[name]
        if isLiteral(result):
            return result
        raise AttributeError

    def setLiteral(self, name, value):
        self._props[name] = value

    def literalKeys(self):
        return (k for k, v in self._props.items() if isLiteral(v))

    def literalValues(self):
        return (v for v in self._props.values() if isLiteral(v))

    def literalItems(self):
        return ((k, v) for k, v in self._props.items() if isLiteral(v))



    ### Accessing edge properties

    def addDirectedEdge(self, name, otherNode):
        # otherNode should always be a valid node
        nodeList = tolist(self._props.get(name))
        nodeList.append(otherNode)
        self._props[name] = toresult(nodeList)

    def removeDirectedEdge(self, name, otherNode):
        # otherNode should always be a valid node
        nodeList = tolist(self._props.get(name))
        nodeList.remove(otherNode)
        self._props[name] = toresult(nodeList)

        # TODO: we should have this, right?
        if self._props[name] is None:
            del self._props[name]


    def outgoingEdgeEndpoints(self, name = None):
        if name is None: return self._allOutgoingEdgeEndpoints()
        else:            return self._outgoingEdgeEndpoints(name)

    def _outgoingEdgeEndpoints(self, name):
        # if name is not an edge, we need to throw an exception
        result = self._props[name]
        if not isLiteral(result):
            return toIterator(result)
        raise AttributeError

    def _allOutgoingEdgeEndpoints(self):
        for prop, eps in self.edgeItems():
            for ep in eps:
                yield ep


    def edgeKeys(self):
        return (k for k, v in self._props.items() if not isLiteral(v))

    def edgeValues(self):
        return (toIterator(v) for v in self._props.values() if not isLiteral(v))

    def edgeItems(self):
        return ((k, toIterator(v)) for k, v in self._props.items() if not isLiteral(v))


    # The next methods are overriden for efficiency
    # They should take precedence over their implementation in ObjectNode, as long as the order
    # of inheritance is respected, ie:
    #
    #   class MemoryObjectNode(MemoryNode, ObjectNode): # GOOD
    #   class MemoryObjectNode(ObjectNode, MemoryNode): # BAD

    def keys(self):
        return self._props.keys()

    # FIXME: wrong implementation as the values for edges should be iterators
    #def values(self):
    #    return self._props.values()

    #def items(self):
    #    return self._props.items()

    def updateValidClasses(self):
        if self.graph()._dynamic:
            self._classes = set(cls for cls in ontology._classes.values() if self.isValidInstance(cls))
        else:
            # no need to do anything
            pass


# MemoryNode needs to come before ObjectNode, because we want it to be able to
# override ObjectNode's methods (for optimization, for instance)
class MemoryObjectNode(MemoryNode, ObjectNode):
    def __init__(self, graph, props = [], _classes = set()):
        log.debug('MemoryObjectNode.__init__: props = %s' % str(props))
        super(MemoryObjectNode, self).__init__(graph, props, _classes)
