#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@gmail.com>
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
import glob

class TestIMDB(TestCase):

    def runtestEpisodeIMDB(self, filename):
        query = Graph()
        chain = BlockingChain(EpisodeFilename(), MergeSolver(Episode), EpisodeIMDB(), SimpleSolver(Episode))

        testcases = yaml.load(open(filename).read())

        for filename, expected in testcases.items():
            query.clear()
            query += Media(filename)
            result = chain.solve(query).findAll(Episode)

            if expected:
                self.assertEqual(len(result), 1)
                self.assert_(result[0].contains(Episode(expected)),
                             msg = 'Expected: %s\nReceived %s' % (Episode(expected), result[0]))
            else:
                self.assertEqual(result, [])


# add a single test function for each file contained in the test_imdb/ directory
for filename in glob.glob(join(currentPath(), 'test_imdb', '*.yaml')):
    testName = basename(filename)[0].upper() + basename(filename)[1:-5]
    # dammit what a laborious hack... closure seems to work oddly otherwise...
    fcode = '''
def test%s(self):
    self.runtestEpisodeIMDB('%s')
testFunc = test%s''' % (testName, filename, testName)
    exec(fcode)
    setattr(TestIMDB, 'test' + testName, testFunc)


suite = allTests(TestIMDB)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
