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

import logging
logging.getLogger('smewt').setLevel(logging.WARNING)


from smewttest import *
import glob


tests = '''
/data/Series/Black Adder/Black_Adder_-_1x01_-_The_Foretelling.digitaldistractions.[www.the-realworld.de].avi:
    series     : Black Adder
    season     : 1
    episodeNumber : 1

/data/Series/Black Adder/Black_Adder_-_1x02_-_Born_To_Be_King.digitaldistractions.[www.the-realworld.de].avi:
    series     : Black Adder
    season     : 1
    episodeNumber : 2

/data/Series/Northern Exposure/Northern Exposure - S01E02 - Brains Know-How and Native Intelligence.avi:
    series     : Northern Exposure
    season     : 1
    episodeNumber : 2
'''

def printClass(cls):
    print 'class: %s' % cls.__name__
    print 'parent: %s' % cls.parentClass().__name__
    print 'schema', cls.schema
    print 'implicit', cls.schema._implicit
    print 'rlookup', cls.reverseLookup


class TestEpisodeFilename(TestCase):

    def withSolver(self, solver):
        data = yaml.load(tests)

        for filename, md in data.items():
            query = MemoryObjectGraph()
            query.Media(filename = unicode(filename))

            schain = BlockingChain(EpisodeFilename(), solver)
            result = schain.solve(query).findAll(Episode)

            self.assertEqual(len(result), 1, 'Solver coudn\'t solve anything...')
            result = result[0]

            for key, value in md.items():
                if key == 'series':
                    self.assertEqual(result.series.title, value)
                else:
                    self.assertEqual(result.get(key), value)


    def testMergeSolver(self):
        self.withSolver(MergeSolver(Episode))

    #def testNaiveSolver(self):
    #    self.withSolver(NaiveSolver(Episode))



suite = allTests(TestEpisodeFilename)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
