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
from smewt import *
from smewt.guessers.episodefilename import EpisodeFilename
from smewt.solvers.naivesolver import NaiveSolver
from smewt.solvers.mergesolver import MergeSolver
import glob
from PyQt4.QtCore import *

tests = '''
/data/Series/Black Adder/Black_Adder_-_1x01_-_The_Foretelling.digitaldistractions.[www.the-realworld.de].avi:
    serie      : Black Adder
    season     : 1
    episodeNumber : 1

/data/Series/Black Adder/Black_Adder_-_1x02_-_Born_To_Be_King.digitaldistractions.[www.the-realworld.de].avi:
    serie      : Black Adder
    season     : 1
    episodeNumber : 2

/data/Series/Northern Exposure/Northern Exposure - S01E02 - Brains Know-How and Native Intelligence.avi:
    serie      : Northern Exposure
    season     : 1
    episodeNumber : 2
'''

class TestEpisodeFilename(TestCase):

    def withSolver(self, solver):
        data = yaml.load(tests)

        for filename, md in data.items():
            query = Collection()
            query.media = [ Media(filename) ]

            schain = SolvingChain(EpisodeFilename(), solver)
            result = schain.launchAndWait(query)

            self.assertEqual(len(result.metadata), 1, 'Solver coudn\'t solve anything...')
            result = result.metadata[0]

            for key, value in md.items():
                self.assertEqual(result[key], value)



    def testMergeSolver(self):
        self.withSolver(MergeSolver())

    def testNaiveSolver(self):
        self.withSolver(NaiveSolver())



suite = allTests(TestEpisodeFilename)

if __name__ == '__main__':
    import sys, logging
    a = QCoreApplication(sys.argv)
    logging.basicConfig(level = logging.DEBUG)
    TextTestRunner(verbosity=2).run(suite)
