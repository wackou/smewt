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

import types
import logging

log = logging.getLogger('smewt.datamodel.AbstractNode')



class AbstractNode(object):
    """This class describes a basic node in a directed graph, with the addition that it has a special
    property "classes" which describe which class this node can "morph" into. This mechanism could be
    built as another basic node property, but it is not for performance reasons.

    It can also have named directed edges to other nodes, ie: the edges are not "anonymous", but are
    first-class citizens (in future versions, we might even want to add other properties to an edge).
    A node can have any number of edges of the same type to other nodes (even multiples edges to the
    same node), but it can't have edges to itself.

    The AbstractNode class is the basic interface one needs to implement for providing
    a backend storage of the data. It is complementary to the AbstractDirectedGraph interface.

    You only need to provide the implementation for this interface, and then an ObjectNode can
    be automatically built upon it.

    The methods you need to implement fall into the following categories:
     - add / remove / clear / check / get current valid classes
     - get / set / iterate over literal properties
     - add / remove / iterate over edges

    Note: as ObjectNode reimplements the __setattr__ method, you have to do the same in your
          subclass of AbstractNode to catch the instance attributes you need to be able to set.
          Failure to do this will most certainly result in an infinite loop, ie: it looks like
          everything is stuck very soon, or even a stack overflow due to infinite recursion.

    """

    def __init__(self, graph, props = []):
        log.debug('AbstractNode.__init__: graph = %s' % str(graph))


    def __eq__(self, other):
        """Return whether two nodes are equal.

        This should implement identity of nodes, not properties equality (this should be done
        in the BaseObject instance)."""
        raise NotImplementedError

    def __hash__(self):
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


    ### Methods related to getting / setting literal properties

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


    ### Methods related to getting / setting edges (edge properties that point to other nodes)

    def addDirectedEdge(self, name, otherNode):
        raise NotImplementedError

    def removeDirectedEdge(self, name, otherNode):
        raise NotImplementedError

    def outgoingEdgeEndpoints(self, name = None):
        """Return all the nodes which this node points to with the given edge type.
        If name is None, return all outgoing edge points."""
        # Note: it is *imperative* that this function return a generator and not just any iterable over the values
        raise NotImplementedError

    def edgeKeys(self):
        # NB: this should return an iterator
        raise NotImplementedError

    def edgeValues(self):
        # NB: this should return an iterator
        # Note: it is *imperative* that this function return a generator for each value and not just any iterable over the values
        raise NotImplementedError

    def edgeItems(self):
        # NB: this should return an iterator
        # Note: it is *imperative* that this function return a generator for each value and not just any iterable over the values
        raise NotImplementedError


    ### Additional utility methods

    def sameProperties(self, other, props = None, exclude = []):
        # NB: sameValidProperties and sameUniqueProperties should be defined in BaseObject
        # TODO: this can surely be optimized
        if props is None:
            props = other.items()
        else:
            props = [ (p, other.get(p)) for p in props ]

        for name, value in props:
            if name in exclude:
                continue
            if isinstance(value, types.GeneratorType):
                svalue = list(self.get(name))
                value = list(value)

                # FIXME: v1.virtual() should not be used here...
                result = (len(svalue) == len(value) and
                          all(v1.virtual() == v2.virtual() for v1, v2 in zip(svalue, value)))

                if result is False:
                    return False
            else:
                if self.get(name) != value:
                    return False

        return True

    def unlinkAll(self):
        for name, nodes in self.edgeItems():
            for n in nodes:
                self.removeDirectedEdge(name, n)
                for oname, onodes in n.edgeItems():
                    for n2 in onodes:
                        if n2 == self:
                            n.removeDirectedEdge(oname, self)
