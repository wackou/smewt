#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2010 Nicolas Wack <wackou@gmail.com>
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

from smewttest import *


def printClass(cls):
    print 'class: %s' % cls.__name__
    print 'parent: %s' % cls.parent_class().__name__
    print 'schema', cls.schema
    print 'implicit', cls.schema._implicit
    print 'rlookup', cls.reverse_lookup

class TestInheritance(TestCase):

    def setUp(self):
        ontology.clear()

    def testSchema(self):
        class A(BaseObject):
            schema = { 'a': int }
            valid = []

        self.assertEqual(len(A.schema), 1)
        self.assertEqual(A.schema['a'], int)

        class B(A):
            schema = { 'b': unicode }
            valid = []

        self.assertEqual(len(A.schema), 1)
        self.assertEqual(A.schema['a'], int)

        self.assertEqual(len(B.schema), 2)
        self.assertEqual(B.schema['a'], int)
        self.assertEqual(B.schema['b'], unicode)

        class C(A):
            schema = { 'c': float }
            valid = []

        self.assertEqual(len(A.schema), 1)
        self.assertEqual(A.schema['a'], int)

        self.assertEqual(len(B.schema), 2)
        self.assertEqual(B.schema['a'], int)
        self.assertEqual(B.schema['b'], unicode)

        self.assertEqual(len(C.schema), 2)
        self.assertEqual(C.schema['a'], int)
        self.assertEqual(C.schema['c'], float)

        def multi():
            class D(B, C):
                schema = {}
                valid = []


        self.assertRaises(TypeError, multi)


    def testImplicitSchema(self):
        class A(BaseObject):
            schema = { 'a': int }
            valid = [ 'a' ]

        class E(A):
            schema = {}
            valid = [ 'a' ]

        class B(BaseObject):
            schema = { 'b': float }
            valid = [ 'b' ]

        def testValidVar():
            class B2(B):
                schema = {}
                valid = []

        self.assertRaises(TypeError, testValidVar)

        class C(B):
            schema = { 'friend': A }
            valid = [ 'b' ]
            reverse_lookup = { 'friend': 'friendOf' }

        self.assertEqual(C.schema['friend'], A)
        self.assert_('friend' not in C.schema._implicit)

        class D(A):
            schema = {}
            valid = [ 'a' ]

        self.assertEqual(C.schema['friend'], A)
        self.assert_('friend' not in C.schema._implicit)

        self.assertEqual(D.schema['friendOf'], C)
        self.assertEqual(E.schema['friendOf'], C)
        self.assertEqual(list(D.schema._implicit), ['friendOf'])
        self.assertEqual(list(E.schema._implicit), ['friendOf'])
        self.assertEqual(D.reverse_lookup, { 'friendOf': 'friend' })
        self.assertEqual(E.reverse_lookup, { 'friendOf': 'friend' })


    def testStaticInheritance(self):
        class A(BaseObject):
            schema = { 'a': int }
            valid = []

        class B(BaseObject):
            schema = { 'b': float }
            valid = []

        g = MemoryObjectGraph(dynamic = True)
        b = g.B()
        self.assert_(A in b.node._classes)

        g = MemoryObjectGraph(dynamic = False)
        b = g.B()
        self.assert_(A not in b.node._classes)


suite = allTests(TestInheritance)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    smewt.shutdown()
