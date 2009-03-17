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

from PyQt4.QtCore import SIGNAL,  QObject
from smewt import Media, Graph
from smewt.media.series import Episode
from smewt.utils import GlobDirectoryWalker

class Importer(QObject):
    def __init__(self, tagger, filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]):
        super(Importer, self).__init__()

        self.taggingQueue = []
        self.tagger = tagger
        self.filetypes = filetypes
        self.results = Graph()
        self.tagCount = 0
        self.state = 'stopped'
        self.connect(self.tagger, SIGNAL('tagFinished'), self.tagged)

    def importFolder(self,  folder):
        for filename in GlobDirectoryWalker(folder, self.filetypes):
            mediaObject = Media(filename)
            self.taggingQueue.append(mediaObject)

        self.tagCount += len(self.taggingQueue)
        self.emit(SIGNAL('progressChanged'),  self.tagCount - len(self.taggingQueue),  self.tagCount)

    def start(self):
        if self.state != 'running':
            self.state = 'running'
            self.tagNext()

    def tagNext(self):
        if self.taggingQueue:
            next = self.taggingQueue.pop()
            #print 'Collection: Tagging ''%s'' %s' % (next, self.tagger.__class__)
            self.tagger.tag(next)
            self.emit(SIGNAL('progressChanged'),  self.tagCount - len(self.taggingQueue),  self.tagCount)
        else:
            self.state = 'stopped'
            self.tagCount = 0
            self.emit(SIGNAL('progressChanged'),  self.tagCount - len(self.taggingQueue),  self.tagCount)
            self.emit(SIGNAL('importFinished'),  self.results)

    def tagged(self, taggedMedia):
        #print 'Collection: Media tagged: %s' % taggedMedia
        self.results += taggedMedia
        self.tagNext()
