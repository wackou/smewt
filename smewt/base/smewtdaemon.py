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

from PyQt4.QtCore import QSettings, QVariant
import smewt
from smewt.media import Series, Episode, Movie
from smewt.base import LocalCollection
from smewt.base.taskmanager import Task, TaskManager
from smewt.base.utils import smewtUserDirectory
from os.path import join, dirname, splitext
from smewt.taggers import EpisodeTagger, MovieTagger
import logging

log = logging.getLogger('smewt.base.smewtdaemon')


class SmewtDaemon(object):
    def __init__(self, progressCallback = None):
        super(SmewtDaemon, self).__init__()

        # FIXME: this is a lame hack to save the collection when we can...
        def callback(current, total):
            if total == 0:
                self.saveCollection()
            if progressCallback is not None:
                progressCallback(current, total)

        self.taskManager = TaskManager(progressCallback = callback)

        settings = QSettings()
        cfile = unicode(settings.value('collection_file').toString())
        if not cfile:
            cfile = join(smewtUserDirectory(), smewt.APP_NAME + '.collection')
            settings.setValue('collection_file', QVariant(cfile))

        csettings = unicode(settings.value('collection_settings').toString())
        if not csettings:
            csettings = join(smewtUserDirectory(), smewt.APP_NAME + '.collection_settings')
            settings.setValue('collection_settings', QVariant(csettings))


        self.collection = LocalCollection(taskManager = self.taskManager, settingsFile = csettings)
        #self.connect(self.collection, SIGNAL('updated'),
        #             self.refreshCollectionView)
        #self.connect(self.collection, SIGNAL('updated'),
        #             self.saveCollection)

        try:
            self.collection.load(cfile)
        except:
            log.warning('Could not load collection %s', cfile)

    def saveCollection(self):
        cfile = unicode(QSettings().value('collection_file').toString())
        self.collection.save(cfile)

    def shutdown(self):
        self.saveCollection()

    def quit(self):
        self.taskManager.abortAll()

    def updateCollection(self):
        self.collection.update()

    def rescanCollection(self):
        self.collection.rescan()

