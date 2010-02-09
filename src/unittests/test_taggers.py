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

logging.getLogger('smewt').setLevel(logging.WARNING)



class TestTaggers(TestCase):

    def setUp(self):
        ontology.reloadSavedOntology('media')

    def testMovieTagger(self):
        #data = yaml.load(movietests)
        pass

    '''
    def testSimple(self):
        data = yaml.load(tests)

        #print data.items()
        for filename, md in data.items():
            print 'testing', filename
            query = MemoryObjectGraph()
            query.Media(filename = unicode(filename))

            schain = BlockingChain(MovieFilename(), MovieIMDB())
            result = schain.solve(query).findAll(Movie)

            self.assertEqual(len(result), 1, 'Solver coudn\'t solve anything...')
            result = result[0]

            for key, value in md.items():
                self.assertEqual(result.get(key), value)

            from smewt.base import cache
            cache.save('/tmp/smewt.cache')
    '''


suite = allTests(TestTaggers)

from smewt.base import cache
cache.load('/tmp/smewt.cache')

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    cache.save('/tmp/smewt.cache')
