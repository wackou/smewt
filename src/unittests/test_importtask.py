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
from smewt.base import TaskManager
from smewt.base.importtask import ImportTask
from smewt.taggers import *
import glob

logging.getLogger('smewt').setLevel(logging.WARNING)
logging.getLogger('smewt.datamodel').setLevel(logging.WARNING)



class TestImportTask(TestCase):

    def setUp(self):
        ontology.reloadSavedOntology('media')

    def createTasks(self, collection):
        t1 = ImportTask(collection, EpisodeTagger, 'Monk/Monk.2x05.Mr.Monk.And.The.Very,.Very.Old.Man.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].avi')
        t2 = ImportTask(collection, EpisodeTagger, 'Monk/Monk.2x05.Mr.Monk.And.The.Very,.Very.Old.Man.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].English.srt')
        t3 = ImportTask(collection, EpisodeTagger, 'Monk/Monk.2x06.Mr.Monk.Goes.To.The.Theater.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].avi')
        t4 = ImportTask(collection, EpisodeTagger, 'Monk/Monk.2x06.Mr.Monk.Goes.To.The.Theater.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].English.srt')

        return t1, t2, t3, t4

    def collectionTest(self, collection):
        series = collection.findAll(Series)
        eps = collection.findAll(Episode)
        subs = collection.findAll(Subtitle)

        self.assertEqual(len(series), 1)
        self.assertEqual(len(eps), 2)
        self.assertEqual(len(subs), 2)

    def testImportEpisodes(self):
        collection = MemoryObjectGraph()

        t1, t2, t3, t4 = self.createTasks(collection)

        t1.perform()
        #collection.displayGraph()
        t2.perform()
        #collection.displayGraph()
        t3.perform()
        #collection.displayGraph()
        t4.perform()
        #collection.displayGraph()

        self.collectionTest(collection)

    def testTaskManager(self):
        collection = MemoryObjectGraph()

        tm = TaskManager()
        for task in self.createTasks(collection):
            tm.add(task)

        # the TaskManager might already have started to process a task, in which case the queue size is 3
        self.assert_(tm.qsize() >= 3)
        self.assert_(tm.total == 4)

        tm.join()

        self.assert_(tm.empty())
        self.assertEqual(tm.total, 0)

        #collection.displayGraph()

        self.collectionTest(collection)

suite = allTests(TestImportTask)

from smewt.base import cache
cache.load('/tmp/smewt.cache')

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    cache.save('/tmp/smewt.cache')
