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

import logging

log = logging.getLogger('smewt.datamodel.AbstractNode')



class AbstractNode(object):
    """This is the class one should inherit from when providing a specific implementation of a Node.

    You need only implement those methods which are necessary to be defined for a node that can have
    literal properties and named edges to other nodes in a directed graph.
    These are signaled in this interface by raising NotImplementedError."""

    def __init__(self, graph, props = []):
        log.debug('AbstractNode.__init__: graph = %s' % str(graph))
        self._graph = graph


    def __eq__(self, other):
        # This should implement identity of nodes, not properties equality (this should be done
        # in the BaseObject instance)
        raise NotImplementedError

    ### Methods needed for storing the nodes ontology (caching)
    ### Note: this could be implemented only using literal values, but it is left
    ###       as part of the API as this is something which is used a lot and benefits
    ###       a lot from being optimized, which can be more easily done in the implementation

    def addClass(self, cls):
        """Add the given class to the list of valid classes for this node."""
        raise NotImplementedError

    def removeClass(self, cls):
        """Remove the given class from the list of valid classes for this node."""
        raise NotImplementedError

    def clearClasses(self):
        """Clears the current list of valid classes."""
        raise NotImplementedError

    def classes(self):
        """Returns an iterator over the list of classes."""
        raise NotImplementedError

    def isinstance(self, cls):
        raise NotImplementedError




    def getLiteral(self, name):
        raise NotImplementedError

    def setLiteral(self, name, value):
        """Need to be implemented by implementation subclass.
        Can assume that literal is always one of the valid literal types."""
        raise NotImplementedError

    def literalKeys(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def literalValues(self):
        raise NotImplementedError

    def literalItems(self):
        raise NotImplementedError


    def addDirectedEdge(self, name, otherNode):
        raise NotImplementedError

    def removeDirectedEdge(self, name, otherNode):
        raise NotImplementedError

    def outgoingEdgeEndpoints(self, name = None):
        """Return all the nodes which this node points to with the given edge type.
        If name is None, return all outgoing edge points."""
        raise NotImplementedError

    def edgeKeys(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def edgeValues(self):
        # TODO: should return an iterator of (iterator on AbstractNodes)
        raise NotImplementedError

    def edgeItems(self):
        raise NotImplementedError

    def sameProperties(self, other, exclude = []):
        # NB: sameValidProperties and sameUniqueProperties should be defined in BaseObject
        # TODO: this can surely be optimized
        for name, value in other.items():
            if name in exclude:
                continue
            if self.get(name) != value:
                return False

        return True
