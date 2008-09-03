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
from smewt.solvers import *
from smewt.guessers import *
import yaml
import glob
from smewt.media import Episode

class TestIMDB(TestCase):

    def testRegression(self):
        for filename in glob.glob('test_imdb/*.yaml'):
            data = yaml.load(open(filename).read())
            #print data


    def testEpGuides(self):
        query = Collection()
        chain = SolvingChain(EpisodeFilename(), MergeSolver(), EpGuides(), SimpleSolver())

        query.media = [ Media('/data/Series/Futurama/Season 1/Futurama.Extras.-.Trailer.DVDRiP-frankysan.[tvu.org.ru].ogm') ]
        result = chain.launchAndWait(query)
        self.assertEqual(result.metadata, [None])

        query.media = [ Media('/data/Series/Futurama/Season 1/Futurama.1x03.I,.Roommate.DVDRiP-frankysan.[tvu.org.ru].ogm') ]
        expected = Episode.fromDict(yaml.load('''
serie : Futurama
season     : 1
episodeNumber : 3
title      : I, Roommate'''))

        result = chain.launchAndWait(query)
        self.assert_(result.metadata[0].contains(expected))

suite = allTests(TestIMDB)

if __name__ == '__main__':
    from PyQt4.QtCore import QCoreApplication
    import sys
    a = QCoreApplication(sys.argv)
    TextTestRunner(verbosity=2).run(suite)
