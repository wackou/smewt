#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2010 Nicolas Wack <wackou@gmail.com>
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

from smewt import SmewtException, SmewtUrl, Graph, Media, Metadata
from smewt.media import Series, Episode, Movie
from smewt.base import ImportTask, SubtitleTask, LocalCollection, ActionFactory
from smewt.base.taskmanager import Task, TaskManager
import logging
from os.path import join, dirname, splitext
from smewt.taggers import EpisodeTagger, MovieTagger

log = logging.getLogger('smewt.base.smewtdaemon')


class SmewtDaemon(object):
    def __init__(self):
        super(SmewtDaemon, self).__init__()

        self.taskManager = TaskManager()

        settings = QSettings()
        t = settings.value('collection_file').toString()
        if t == '':
            t = join(dirname(unicode(settings.fileName())),  'Smewg.collection')
            settings.setValue('collection_file',  QVariant(t))


        self.collection = LocalCollection(taskManager = self.taskManager)
        #self.connect(self.collection, SIGNAL('updated'),
        #             self.refreshCollectionView)
        #self.connect(self.collection, SIGNAL('updated'),
        #             self.saveCollection)

        try:
            self.collection.load(t)
        except:
            log.warning('Could not load collection %s', t)
            raise


    def shutdown(self):
        self.saveCollection()

    def quit(self):
        self.taskManager.abortAll()

    def updateCollection(self):
        self.collection.update()

    def rescanCollection(self):
        self.collection.rescan()

