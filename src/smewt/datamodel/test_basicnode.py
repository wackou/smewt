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
from memoryobjectgraph import MemoryObjectGraph
from baseobject import BaseObject, Schema
from utils import tolist
import ontology
import unittest

class TestBasicNode(unittest.TestCase):

    def setUp(self):
        # FIXME: clear the previous ontology because the graphs do not get GC-ed properly
        ontology.clear()

    def testBasicNode(self):
        g = BasicGraph()

        n = g.createNode()
        n.setLiteral('title', u'abc')
        self.assertEqual(n.getLiteral('title'), u'abc')
        self.assertEqual(list(n.literalKeys()), [ 'title' ])
        self.assertEqual(list(n.edgeKeys()), [])

        n2 = g.createNode()
        n.setLink('friend', n2)
        n2.setLink('friend', n)
        self.assertEqual(n.getLiteral('title'), u'abc')
        self.assertEqual(list(n.literalKeys()), [ 'title' ])
        self.assertEqual(list(n.edgeKeys()), [ 'friend' ])
        self.assertEqual(list(n.outgoingEdgeEndpoints('friend')), [ n2 ])
        self.assertEqual(list(n2.outgoingEdgeEndpoints('friend')), [ n ])


    def testBasicObjectNode(self):
        g = BasicGraph()

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
        self.assertEqual(list(n.friend), [ n ])
        self.assertEqual(list(n2.isFriendOf), [ n ])


    def testMRO(self):
        class A(object):
            def __init__(self):
                print 'A.__init__()'

        class B(A):
            def __init__(self):
                A.__init__(self)
                print 'B.__init__()'

        class C(A):
            def __init__(self):
                A.__init__(self)
                print 'C.__init__()'

        class D(B, C):
            def __init__(self):
                B.__init__(self)
                C.__init__(self)
                print 'D.__init__()'

        d = D()

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicNode)

    import logging
    logging.getLogger('smewt').setLevel(logging.WARNING)
    logging.getLogger('smewt.datamodel.Ontology').setLevel(logging.ERROR)
    #logging.getLogger('smewt.datamodel.ObjectNode').setLevel(logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite)
