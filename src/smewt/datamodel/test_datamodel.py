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
from ontology import BaseObject, OntologyManager
import unittest

class TestObjectNode(unittest.TestCase):

    def testBasicObjectNode(self):
        n1 = ObjectNode(BaseObject)
        self.assertEquals(n1.keys(), [])

        n1.title = 'abc'
        self.assertEquals(n1.title, 'abc')

        n2 = ObjectNode(BaseObject, title = 'abc')
        self.assertEquals(n2.title, 'abc')
        self.assertEquals(n1, n2)

        n1.sameas = n2
        self.assertEquals(n1.sameas, n2)

        n2.plot = 'empty'
        self.assertEquals(n1.sameas.title, 'abc')
        self.assertEquals(n1.sameas.plot, 'empty')

    def testBasicOntology(self):
        class A(BaseObject):
            schema = { 'a': int  }
            unique = [ 'a' ]

        class B(A):
            pass

        class C(BaseObject):
            schema = { 'c': int  }
            unique = [ 'c' ]

        class D(BaseObject):
            pass

        class E:
            schema = { 'e': int  }
            unique = [ 'e' ]

        self.assertEquals(issubclass(A, BaseObject), True)
        self.assertEquals(issubclass(B, A), True)
        self.assertEquals(issubclass(A, A), True)
        self.assertEquals(issubclass(A, B), False)
        self.assertEquals(issubclass(B, BaseObject), True)
        self.assertEquals(issubclass(C, A), False)
        self.assertEquals(B.parentClass().className(), 'A')

        OntologyManager.register(A, B, C)
        self.assertRaises(TypeError, OntologyManager.register, D)
        self.assertRaises(TypeError, OntologyManager.register, E)

        self.assert_(OntologyManager.getClass('A') is A)
        self.assertRaises(ValueError, OntologyManager.getClass, 'D')
        self.assert_(OntologyManager.getClass('B').parentClass().parentClass() is BaseObject)

        # test instance creation
        a = A(title = 'Scrubs', epnum = 5)

        print type(a), a
        self.assertEquals(type(a), ObjectNode)
        self.assertEquals(a._class, A)
        self.assertEquals(a._class.className(), 'A')

    def testValidUniqueMethods(self):
        class Episode(BaseObject):
            schema = { 'series': str,
                       'season': int,
                       'epnum': int,
                       'title': str
                       }

            unique = [ 'series', 'season', 'epnum' ]

        ep = Episode(series = 'House M.D.', season = 3, epnum = 2)
        self.assertEquals(ep.isValid(), True)
        ep.title = 'gloub'
        ep.gulp = 'gloubiboulga'
        self.assertEquals(ep.isValid(), True)
        ep.title = 3
        self.assertEquals(ep.isValid(), False)

        self.assertEquals(ep.isUnique(), True)
        self.assertEquals(Episode(series='abc').isUnique(), False)

    def testChainedAttributes(self):
        #a = findAll(Episode, series__title = 'Scrubs')
        pass

if __name__ == '__main__':
    unittest.main()
