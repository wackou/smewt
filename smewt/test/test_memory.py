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


from smewttest import *

class TestMemory(TestCase):

    def setUp(self):
        ontology.clear()

    def testGraphGC(self):
        ontology._graphs.clear()

        def f():
            g = MemoryObjectGraph()

        f()
        # as the graph came out of scope, it should be GC'ed
        self.assertEqual(ontology._graphs.items(), [])

        def g():
            g = MemoryObjectGraph()
            o = g.BaseObject(a = 3)

        g()
        # as the graph came out of scope, it should be GC'ed
        self.assertEqual(ontology._graphs.items(), [])

        g = MemoryObjectGraph()
        o1 = g.BaseObject(a = 3)
        o2 = g.BaseObject(b = 2, c = o1)

        self.assertEqual(len(ontology._graphs.items()), 1)

        del g
        self.assertEqual(ontology._graphs.items(), [])


suite = allTests(TestMemory)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    shutdown()
