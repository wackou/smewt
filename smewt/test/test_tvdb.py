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

class TestTVDB(TestCase):

    def setUp(self):
        ontology.reload_saved_ontology('media')

    def runtestEpisodeTVDB(self, filename):
        query = MemoryObjectGraph()
        chain = SolvingChain(EpisodeFilename(), MergeSolver(Episode), EpisodeTVDB(), SimpleSolver(Episode))

        testcases = yaml.load(open(filename).read())

        for filename, expected in testcases.items():
            query.clear()
            query.Media(filename = filename)
            result = chain.solve(query).find_all(Episode)

            if expected:
                self.assertEqual(len(result), 1)
                result = result[0]
                for key, value in expected.items():
                    if key == 'series':
                        self.assertEqual(result.series.title, value)
                    else:
                        self.assertEqual(result.get(key), value,
                                         msg = 'Expected: %s\nReceived %s' % (expected, result))
            else:
                self.assertEqual(result, [])


# add a single test function for each file contained in the test_imdb/ directory
for filename in glob.glob(join(currentPath(), 'test_tvdb', '*.yaml')):
    if filename.endswith('blackadder.yaml'):
        continue

    testName = basename(filename)[0].upper() + basename(filename)[1:-5]
    # dammit what a laborious hack... closure seems to work oddly otherwise...
    fcode = '''
def test%s(self):
    self.runtestEpisodeTVDB('%s')
testFunc = test%s''' % (testName, filename, testName)
    exec(fcode)
    setattr(TestTVDB, 'test' + testName, testFunc)


suite = allTests(TestTVDB)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    smewt.shutdown()

