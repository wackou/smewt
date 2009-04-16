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
from smewt.base import Media, Graph, Task
from smewt.media.series import Episode
from smewt.base.utils import GlobDirectoryWalker
import logging

log = logging.getLogger('smewt.importtask')

class ImportTask(QThread, Task):
    def __init__(self, folder, tagger, filetypes):
        super(ImportTask, self).__init__()
        self.filetypes = filetypes
        self.totalCount = 0
        self.progressedCount = 0
        self.folder = folder
        self.tagger = tagger
        
    def total(self):
        return self.totalCount

    def progressed(self):
        return self.progressedCount


    def run(self):
        self.worker = Worker(self.folder, self.tagger, self.filetypes)

        self.connect(self.worker, SIGNAL('progressChanged'),
                     self.progressChanged)

        self.connect(self.worker, SIGNAL('foundData'),
                     self.foundData)

        self.connect(self.worker, SIGNAL('importFinished'),
                     self.importFinished)

        self.worker.begin()

        self.exec_()

    def __del__(self):
        self.wait()
    
    def importFinished(self, results):
        self.emit(SIGNAL('foundData'), results)
        self.emit(SIGNAL('taskFinished'), self)

    def progressChanged(self, current, total):
        self.progressedCount = current
        self.totalCount = total
        self.emit(SIGNAL('progressChanged'))

    def foundData(self, md):
        self.emit(SIGNAL('foundData'), md)


class Worker(QObject):
    def __init__(self, folder, tagger, filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]):
        super(Worker, self).__init__()
        self.filetypes = filetypes
        self.taggingQueue = []
        self.taggers = {}
        self.results = Graph()
        self.tagCount = 0
        self.state = 'stopped'

        for filename in GlobDirectoryWalker(folder, self.filetypes):
            mediaObject = Media(filename)
            self.taggingQueue.append(( tagger, mediaObject ))
            self.tagCount += 1
            
    def begin(self):
        if self.state != 'running':
            self.state = 'running'
            self.tagNext()


    def tagNext(self):
        if self.taggingQueue:
            tagger, next = self.taggingQueue.pop()
            self.emit(SIGNAL('progressChanged'), self.tagCount - len(self.taggingQueue),  self.tagCount)
            
            if tagger not in self.taggers:
                self.taggers[tagger] = tagger()
                self.connect(self.taggers[tagger], SIGNAL('tagFinished'), self.tagged)

            self.taggers[tagger].tag(next)
                  
        else:
            self.state = 'stopped'
            self.tagCount = 0
            self.emit(SIGNAL('progressChanged'), self.tagCount - len(self.taggingQueue),  self.tagCount)
            self.emit(SIGNAL('foundData'), self.results)
            self.emit(SIGNAL('importFinished'), self.results)
            self.results = Graph()

    def tagged(self, taggedMedia, send = False):
        log.info('Media tagged: %s' % taggedMedia)
        self.results += taggedMedia            
        self.tagNext()
