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
from objectgraph import ObjectGraph, Equal
from memoryobjectgraph import MemoryGraph, MemoryObjectGraph
from baseobject import BaseObject, Schema
from utils import tolist
import ontology
import unittest

class TestAbstractNode(unittest.TestCase):

    def setUp(self):
        # FIXME: clear the previous ontology because the graphs do not get GC-ed properly
        ontology.clear()

    def atestAbstractNode(self, GraphClass = MemoryGraph):
        g = GraphClass()

        n = g.createNode()
        n.setLiteral('title', u'abc')
        self.assertEqual(n.getLiteral('title'), u'abc')
        self.assertEqual(list(n.literalKeys()), [ 'title' ])
        self.assertEqual(list(n.edgeKeys()), [])

        n2 = g.createNode()
        n.addDirectedEdge('friend', n2)
        n2.addDirectedEdge('friend', n)
        self.assertEqual(n.getLiteral('title'), u'abc')
        self.assertEqual(list(n.literalKeys()), [ 'title' ])
        self.assertEqual(list(n.edgeKeys()), [ 'friend' ])
        self.assertEqual(list(n.outgoingEdgeEndpoints('friend')), [ n2 ])
        self.assertEqual(list(n2.outgoingEdgeEndpoints('friend')), [ n ])

        n3 = g.createNode()
        n.addDirectedEdge('friend', n3)
        n3.addDirectedEdge('friend', n)
        self.assertEqual(len(list(n.outgoingEdgeEndpoints('friend'))), 2)
        self.assertEqual(len(list(n.outgoingEdgeEndpoints())), 2)
        self.assert_(n2 in n.outgoingEdgeEndpoints('friend'))
        self.assert_(n3 in n.outgoingEdgeEndpoints('friend'))


    def atestBasicObjectNode(self, ObjectGraphClass = MemoryObjectGraph):
        g = ObjectGraphClass()

        n = g.createNode()
        n.title = u'abc'
        self.assertEqual(n.getLiteral('title'), u'abc')
        self.assertEqual(list(n.literalKeys()), [ 'title' ])
        self.assertEqual(list(n.edgeKeys()), [])

        n2 = g.createNode()
        n.friend = n2
        self.assertEqual(n.title, u'abc')
        self.assertEqual(list(n.literalKeys()), [ 'title' ])
        self.assertEqual(list(n.edgeKeys()), [ 'friend' ])
        self.assertEqual(list(n.friend), [ n2 ])
        self.assertEqual(list(n2.isFriendOf), [ n ])


    def testMRO(self):
        class A(object):
            def __init__(self):
                print 'A.__init__()'

            def __contains__(self, obj):
                print 'A.__contains__'

        class B(A):
            def __init__(self):
                super(B, self).__init__()
                print 'B.__init__()'

            #def __contains__(self, obj):
            #    print 'B.__contains__'

        class C(A):
            def __init__(self):
                super(C, self).__init__()
                print 'C.__init__()'

            def __contains__(self, obj):
                print 'C.__contains__'

        class D(B, C):
            def __init__(self):
                super(D, self).__init__()
                print 'D.__init__()'

            #def __contains__(self, obj):
            #    print 'D.__contains__'

        d = D()
        3 in d

    def testBaseObject(self, GraphClass = MemoryObjectGraph):
        class NiceGuy(BaseObject):
            schema = Schema({ 'friend': BaseObject })
            valid = [ 'friend' ]
            reverseLookup = { 'friend': 'friendOf' }

        # There is a problem when the reverse-lookup has the same name as the property because of the types:
        # NiceGuy.friend = BaseObject, BaseObject.friend = NiceGuy
        #
        # it should also be possible to have A.friend = B and C.friend = B, and not be a problem for B, ie: type(B.friend) in [ A, C ]
        #
        # or we should restrict the ontology only to accept:
        #  - no reverseLookup where key == value
        #  - no 2 classes with the same link types to a third class
        # actually, no reverseLookup where the implicit property could override an already existing one

        ontology.register(NiceGuy)

        g1 = GraphClass()
        g2 = GraphClass()

        n1 = g1.BaseObject(a = 23)
        n2 = g1.NiceGuy(friend = n1)

        r2 = g2.addObject(n2)

        n3 = g1.NiceGuy(name = u'other node', friend = n1)
        r3 = g2.addObject(n3)

        # TODO: also try adding n2 after n3 is created

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAbstractNode)

    import logging
    logging.getLogger('smewt').setLevel(logging.WARNING)
    logging.getLogger('smewt.datamodel.Ontology').setLevel(logging.ERROR)
    #logging.getLogger('smewt.datamodel.AbstractDirectedGraph').setLevel(logging.DEBUG)
    #logging.getLogger('smewt.datamodel.ObjectNode').setLevel(logging.DEBUG)
    #logging.getLogger('smewt.datamodel.MemoryObjectNode').setLevel(logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite)