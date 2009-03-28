#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from PyQt4.QtCore import SIGNAL, Qt, QObject, QThread
from smewt import Media, Graph
from smewt.media.series import Episode
from smewt.base.utils import GlobDirectoryWalker
import logging

log = logging.getLogger('smewt.importer')

class Importer(QThread):
    def __init__(self, filetypes):
        super(Importer, self).__init__()
        self.filetypes = filetypes

    def run(self):
        self.worker = Worker(self, self.filetypes)
        self.connect(self, SIGNAL('importFolder'),
                     self.worker.importFolder) #, Qt.QueuedConnection)
        self.exec_()

    def __del__(self):
        self.wait()

    def importFolder(self, folder, tagger):
        self.emit(SIGNAL('importFolder'), folder, tagger)

    def importFinished(self, results):
        self.emit(SIGNAL('importFinished'), results)

    def progressChanged(self, current, total):
        self.emit(SIGNAL('progressChanged'), current, total)

    def foundData(self, md):
        self.emit(SIGNAL('foundData'), md)


class Worker(QObject):
    def __init__(self, importer, filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]):
        super(Worker, self).__init__()
        self.importer = importer
        self.filetypes = filetypes
        self.taggingQueue = []
        self.taggers = {}
        self.results = Graph()
        self.tagCount = 0
        self.state = 'stopped'

    def importFolder(self, folder, tagger):
        for filename in GlobDirectoryWalker(folder, self.filetypes):
            mediaObject = Media(filename)
            self.taggingQueue.append(( tagger, mediaObject ))

        self.tagCount += len(self.taggingQueue)
        self.importer.progressChanged(self.tagCount - len(self.taggingQueue),  self.tagCount)
        self.begin()

    def begin(self):
        if self.state != 'running':
            self.state = 'running'
            self.tagNext()


    def tagNext(self):
        if self.taggingQueue:
            tagger, next = self.taggingQueue.pop()

            if tagger not in self.taggers:
                self.taggers[tagger] = tagger()
                self.connect(self.taggers[tagger], SIGNAL('tagFinished'), self.tagged)

            self.taggers[tagger].tag(next)

            self.importer.progressChanged(self.tagCount - len(self.taggingQueue),  self.tagCount)

        else:
            self.state = 'stopped'
            self.tagCount = 0
            self.importer.progressChanged(self.tagCount - len(self.taggingQueue),  self.tagCount)
            self.importer.importFinished(self.results)

    def tagged(self, taggedMedia):
        log.info('Media tagged: %s' % taggedMedia)
        self.importer.foundData(taggedMedia)
        self.tagNext()
