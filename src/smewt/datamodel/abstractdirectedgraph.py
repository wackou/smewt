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

log = logging.getLogger('smewt.datamodel.AbstractDirectedGraph')


class Equal:
    # some constants
    OnIdentity = 1
    OnValue = 2
    OnValidValue = 3
    OnUnique = 4
    OnLiterals = 5



class AbstractDirectedGraph(object):
    """This class describes a basic directed graph, with the addition that the nodes have a special
    property "classes" which describe which class an node can "morph" into. This mechanism could be
    built as another basic node property, but it is not for performance reasons.

    The AbstractDirectedGraph class is the basic interface one needs to implement for providing
    a backend storage of the data. It is complementary to the AbstractNode interface.

    You only need to provide the implementation for this interface, and then an ObjectGraph can
    be automatically built upon it.

    The methods you need to implement fall into the following categories:
     - create / delete node(s)
     - get all nodes / only nodes from a given class
     - check whether a node lives in a given graph
     - find a node given a list of matching properties

    """

    def clear():
        """Delete all nodes and links in this graph."""
        raise NotImplementedError

    def createNode(self, props = []):
         raise NotImplementedError

    def deleteNode(self, node):
        """Remove a given node.

        strategies for what to do with linked nodes should be configurable, ie:
        remove incoming/outgoing linked nodes as well, only remove link but do not
        touch linked nodes, etc..."""
        raise NotImplementedError

    def nodes(self):
        """Return an iterator on all the nodes in the graph."""
        raise NotImplementedError

    def nodesFromClass(self, cls):
        """Return an iterator on the nodes of a given class."""
        raise NotImplementedError


    def addDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        node.addDirectedEdge(name, otherNode)

    def removeDirectedEdge(self, node, name, otherNode):
        # otherNode should always be a valid node
        node.removeDirectedEdge(name, otherNode)

    def contains(self, node):
        """Return whether this graph contains the given node.

        multiple strategies can be used here for determing object equality, such as
        all properties equal, the primary subset of properties equal, etc... (those are defined
        by the ObjectNode)"""
        raise NotImplementedError

    def __contains__(self, node):
        """Return whether this graph contains the given node (identity)."""
        # TODO: remove this, as it should only be implemented in the ObjectGraph
        raise NotImplementedError


    ### Methods related to a graph serialization

    def toNodesAndEdges(self):
        nodes = {}
        classes = {}
        rnodes = {}
        edges = []

        i = 0
        for n in self.nodes():
            nodes[i] = list(n.literalItems())
            rnodes[id(n)] = i
            classes[i] = [ cls.__name__ for cls in n._classes ]
            i += 1

        for n in self.nodes():
            for prop, links in n.edgeItems():
                for otherNode in links:
                    edges.append((rnodes[id(n)], prop, rnodes[id(otherNode)]))

        return nodes, edges, classes

    def fromNodesAndEdges(self, nodes, edges, classes):
        import ontology

        self.clear()
        idmap = {}
        for _id, node in nodes.items():
            idmap[_id] = self.createNode(props = ((prop, value, None) for prop, value in node),
                                         _classes = (ontology.getClass(cls) for cls in classes[_id]))

        for node, name, otherNode in edges:
            idmap[node].addDirectedEdge(name, idmap[otherNode])

        # TODO: we need to make sure that the current ontology is the saem as when we saved this graph, otherwise
        #       previously set classes might not be valid anymore, or some subclasses won't be correctly set
        # we need to revalidate explicitly, as we might have classes in our ontolo
        #self.revalidateObjects()


    def save(self, filename):
        """Saves the graph to the given filename."""
        import cPickle as pickle
        pickle.dump(self.toNodesAndEdges(), open(filename, 'w'))

    def load(self, filename):
        import cPickle as pickle
        self.fromNodesAndEdges(*pickle.load(open(filename)))

    # __getstate__ and __setstate__ are needed for the cache to be able to work
    def __getstate__(self):
        return self.toNodesAndEdges()

    def __setstate__(self, state):
        # FIXME: this doesn't belong here...
        self._dynamic = False

        self.fromNodesAndEdges(*state)


    ### Utility methods

    def displayGraph(self):
        import cPickle as pickle
        import tempfile
        import subprocess

        nodes, edges, classes = self.toNodesAndEdges()
        fid, filename = tempfile.mkstemp(suffix = '.png')

        dg = []
        dg += [ 'digraph G {' ]

        def tostring(prop):
            if isinstance(prop, list):
                result = u', '.join([ unicode(p) for p in prop ])
            else:
                result = unicode(prop)

            # appply html chars transformation
            result = result.replace('&', '&amp;')

            return result

        for _id, n in nodes.items():
            label = '<FONT COLOR="#884444">%s</FONT><BR/>' % (', '.join(cls for cls in classes[_id] if cls != 'BaseObject') or 'BaseObject')
            label += '<BR/>'.join([ '%s: %s' % (name, tostring(prop)[:32].encode('utf-8')) for name, prop in n ])
            dg += [ 'node_%d [shape=polygon,sides=4,label=<%s>];' % (_id, label) ]

        for node, name, otherNode in edges:
            dg += [ 'node_%d -> node_%d [label="%s"];' % (node, otherNode, name) ]

        dg += [ '}' ]

        subprocess.Popen([ 'dot', '-Tpng', '-o', filename ], stdin = subprocess.PIPE).communicate('\n'.join(dg))

        subprocess.Popen([ 'gwenview', filename ], stdout = subprocess.PIPE, stderr = subprocess.PIPE).communicate()
