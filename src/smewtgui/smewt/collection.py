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
from smewt import Media
from smewt.media.series import Episode
from smewt.utils import GlobDirectoryWalker

class FolderImporter(QObject):
    def __init__(self, folder):
        super(FolderImporter, self).__init__()

        self.folder = folder
        self.taggingQueue = []
        from smewt.taggers.magicepisodetagger import MagicEpisodeTagger
        self.tagger = MagicEpisodeTagger()
        self.results = Collection()

        self.connect(self.tagger, SIGNAL('tagFinished'), self.tagged)

    def start(self):
        # Populate the tagging queue
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv' ] # video files
        for filename in GlobDirectoryWalker(self.folder, filetypes):
            mediaObject = Media(filename)
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
        # TODO: here we should import both the Media and the Metadata into the user
        # collection, we probably need to have a merging algorithm to find out which are already
        # imported, etc...
        self.results.mergeCollection(taggedMedia)
        self.tagNext()

class Collection(QObject):
    '''A Collection instance contains 3 variables:
     - self.media, which contains all the files that are being monitored on the HDD
     - self.metadata, which contains the information about all the AbstractMediaObject
       that Smewt knows of.
     - self.links, which contains the links from elements in self.media to elements
       in self.metadata and which correspond to the files the user has tagged.

    As far as possible, Smewt's job is to collect files from the HDD and put them
    in the self.media variable, get information from the web and fill the
    self.metadata variable, and then use the available guessers/solvers to map
    the entries in self.media to the ones in self.metadata'''

    def __init__(self):
        super(Collection, self).__init__()
        self.media = []
        self.metadata = []
        self.links = []

    def importFolder(self, folder):
        self.folderImporter = FolderImporter(folder)
        self.connect(self.folderImporter, SIGNAL('importFinished'), self.mergeCollection)
        self.folderImporter.start()


    def mergeCollection(self, c):
        #print 'Collection: Adding medias'
        self.media += c.media
        self.metadata += c.metadata
        self.links += c.links
        self.emit(SIGNAL('collectionUpdated'))

    def filter(self, prop, value):
        result = Collection()
        for media, metadata in self.links:
            if metadata[prop] == value:
                result.media += [ media ]
                result.metadata += [ metadata ]
                result.links += [ (media, metadata) ]
        return result


    def load(self, filename):
        import cPickle
        dicts = cPickle.load(open(filename))

        self.media = [ EpisodeObject.fromDict(d) for d in dicts ]

    def save(self, filename):
        import cPickle
        f = open(filename, 'w')
        cPickle.dump(self.media, f)
        cPickle.dump([ m.toDict() for m in self.metadata ], f)
        # FIXME: cannot dump links correctly, need to use reference
        f.close()

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
