#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
# Copyright (c) 2008 Ricard Marxer
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
from media.series.serieobject import EpisodeObject
from smewt.taggers.magicepisodetagger import MagicEpisodeTagger
from smewt.utils import GlobDirectoryWalker

class FolderImporter(QObject):
    def __init__(self, folder):
        super(FolderImporter, self).__init__()

        self.folder = folder
        self.taggingQueue = []
        self.tagger = MagicEpisodeTagger()
        self.results = []

        self.connect(self.tagger, SIGNAL('tagFinished'), self.tagged)

    def start(self):
        # Populate the tagging queue
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv' ] # video files
        for filename in GlobDirectoryWalker(self.folder, filetypes):
            mediaObject = EpisodeObject.fromDict({'filename': filename})
            mediaObject.confidence['filename'] = 1.0
            self.taggingQueue.append(mediaObject)

        self.tagNext()

    def tagNext(self):
        if self.taggingQueue:
            next = self.taggingQueue.pop()
            #print 'Collection: Tagging ''%s''' % next
            self.tagger.tag(next)
        else:
            self.emit(SIGNAL('importFinished'), self.results)

    def tagged(self, taggedMedia):
        #print 'Collection: Media tagged: %s' % taggedMedia
        self.results.append(taggedMedia)
        self.tagNext()

class Collection(QObject):
    def __init__(self):
        super(Collection, self).__init__()
        self.medias = []

    def importFolder(self, folder):
        self.folderImporter = FolderImporter(folder)
        self.connect(self.folderImporter, SIGNAL('importFinished'), self.addMedias)
        self.folderImporter.start()


    def addMedias(self, newMedias):
        #print 'Collection: Adding medias'
        self.medias.extend(newMedias)
        self.emit(SIGNAL('collectionUpdated'))


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    col = Collection()
    col.importFolder(sys.argv[1])

    def printCollection():
        for media in col.medias:
            print media

    app.connect(col, SIGNAL('collectionUpdated'), printCollection)

    app.exec_()
