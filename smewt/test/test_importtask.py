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
from smewt.base import TaskManager, SmewtDaemon
from smewt.base.importtask import ImportTask
from smewt.taggers import *
import glob



class TestImportTask(TestCase):

    def setUp(self):
        ontology.reload_saved_ontology('media')

    def createTasks(self, database):
        t1 = ImportTask(database, EpisodeTagger, 'Monk/Monk.2x05.Mr.Monk.And.The.Very,.Very.Old.Man.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].avi')
        t2 = ImportTask(database, EpisodeTagger, 'Monk/Monk.2x05.Mr.Monk.And.The.Very,.Very.Old.Man.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].English.srt')
        t3 = ImportTask(database, EpisodeTagger, 'Monk/Monk.2x06.Mr.Monk.Goes.To.The.Theater.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].avi')
        t4 = ImportTask(database, EpisodeTagger, 'Monk/Monk.2x06.Mr.Monk.Goes.To.The.Theater.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].English.srt')

        return t1, t2, t3, t4

    def collectionTestIncomplete(self, database):
        self.assertEqual(len(list(database.nodes())), 5)
        series = database.find_all(Series)
        eps = database.find_all(Episode)
        subs = database.find_all(Subtitle)

        self.assertEqual(len(series), 1)
        self.assertEqual(len(eps), 1)
        self.assertEqual(len(subs), 1)

    def collectionTest(self, database):
        self.assertEqual(len(list(database.nodes())), 9)
        series = database.find_all(Series)
        eps = database.find_all(Episode)
        subs = database.find_all(Subtitle)

        self.assertEqual(len(series), 1)
        self.assertEqual(len(eps), 2)
        self.assertEqual(len(subs), 2)

    def testImportEpisodes(self):
        database = MemoryObjectGraph()

        t1, t2, t3, t4 = self.createTasks(database)

        t1.perform()
        #database.display_graph()
        t2.perform()
        #database.display_graph()
        t3.perform()
        #database.display_graph()
        t4.perform()
        #database.display_graph()

        self.collectionTest(database)

    def testImportVobsubSubtitle(self):
        database = MemoryObjectGraph()
        t = ImportTask(database, EpisodeTagger, '/home/download/tmp/testsmewt_series/Arrested_development/Arrested.Development.3x07.Prison.Break-In.DVDRip-TOPAZ.[tvu.org.ru].idx')
        t.perform()
        str(database.find_one(Media))
        #database.display_graph()

    def testTaskManager(self):
        database = MemoryObjectGraph()

        tm = TaskManager()
        for task in self.createTasks(database):
            tm.add(task)

        # the TaskManager might already have started to process a task, in which case the queue size is 3
        self.assert_(tm.queue.qsize() >= 3)
        self.assert_(tm.total == 4)

        tm.queue.join()

        self.assert_(tm.queue.empty())
        self.assertEqual(tm.total, 0)

        #database.display_graph()

        self.collectionTest(database)

    def testSmewtDaemon(self):
        # we need to remove traces of previous test runs, even though we're supposed to have cleaned it after the test,
        # a previous run of the test that failed might not have done that
        os.system('rm -fr ~/.config/DigitalGaia_tmp')
        os.system('rm -fr /tmp/smewt_test_daemon')

        import smewt
        orgname = smewt.ORG_NAME
        appname = smewt.APP_NAME

        smewt.ORG_NAME = 'DigitalGaia_tmp'
        smewt.APP_NAME = 'Smewt_tmp'

        from PyQt4.QtCore import QCoreApplication
        app = QCoreApplication([])
        app.setOrganizationName(smewt.ORG_NAME)
        app.setOrganizationDomain('smewt.com')
        app.setApplicationName(smewt.APP_NAME)

        smewtd = SmewtDaemon()

        # create fake database
        cmds = '''mkdir -p /tmp/smewt_test_daemon/Monk
        touch /tmp/smewt_test_daemon/Monk/Monk.2x05.Mr.Monk.And.The.Very,.Very.Old.Man.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].avi
        touch /tmp/smewt_test_daemon/Monk/Monk.2x05.Mr.Monk.And.The.Very,.Very.Old.Man.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].English.srt
        '''
        for cmd in cmds.split('\n'):
            os.system(cmd.strip())

        smewtd.episodeCollection.folders = { '/tmp/smewt_test_daemon': True }

        # make sure we don't have a residual collection from previous test runs
        self.assertEqual(len(list(smewtd.database.nodes())), 0)

        # initial import of the collection
        smewtd.episodeCollection.rescan()
        smewtd.taskManager.queue.join() # wait for all import tasks to finish

        #smewtd.database.display_graph()
        self.collectionTestIncomplete(smewtd.database)

        # update collection, as we haven't changed anything it should be the same
        smewtd.episodeCollection.update()
        smewtd.taskManager.queue.join() # wait for all import tasks to finish

        #smewtd.database.display_graph()
        self.collectionTestIncomplete(smewtd.database)

        # fully rescan collection, should still be the same
        smewtd.episodeCollection.rescan()
        smewtd.taskManager.queue.join() # wait for all import tasks to finish

        #smewtd.database.display_graph()
        self.collectionTestIncomplete(smewtd.database)

        # add some more files
        cmds = '''mkdir -p /tmp/smewt_test_daemon/Monk
        touch /tmp/smewt_test_daemon/Monk/Monk.2x06.Mr.Monk.Goes.To.The.Theater.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].avi
        touch /tmp/smewt_test_daemon/Monk/Monk.2x06.Mr.Monk.Goes.To.The.Theater.DVDRip.XviD-MEDiEVAL.[tvu.org.ru].English.srt
        '''
        for cmd in cmds.split('\n'):
            os.system(cmd.strip())

        # update collection
        smewtd.episodeCollection.update()
        smewtd.taskManager.queue.join() # wait for all import tasks to finish

        #smewtd.database.display_graph()
        self.collectionTest(smewtd.database)

        # clean up our mess before we exit
        os.system('rm -fr ~/.config/DigitalGaia_tmp')
        os.system('rm -fr /tmp/smewt_test_daemon')

        smewt.ORG_NAME = orgname
        smewt.APP_NAME = appname


suite = allTests(TestImportTask)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    shutdown()
