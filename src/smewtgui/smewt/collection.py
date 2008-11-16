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

class Importer(QObject):
    def __init__(self):
        super(Importer, self).__init__()

        self.taggingQueue = []
        from smewt.taggers.episodetagger import EpisodeTagger
        self.tagger = EpisodeTagger()
        self.results = Collection()
        self.tagCount = 0
        self.state = 'stopped'
        self.connect(self.tagger, SIGNAL('tagFinished'), self.tagged)

    def importFolder(self,  folder):
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ] # video files
        for filename in GlobDirectoryWalker(folder, filetypes):
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
            #print 'Collection: Tagging ''%s''' % next
            self.tagger.tag(next)
            self.emit(SIGNAL('progressChanged'),  self.tagCount - len(self.taggingQueue),  self.tagCount)
        else:
            self.state = 'stopped'
            self.tagCount = 0
            self.emit(SIGNAL('progressChanged'),  self.tagCount - len(self.taggingQueue),  self.tagCount)
            self.emit(SIGNAL('importFinished'),  self.results)

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

    As far as possible, Smewt''s job is to collect files from the HDD and put them
    in the self.media variable, get information from the web and fill the
    self.metadata variable, and then use the available guessers/solvers to map
    the entries in self.media to the ones in self.metadata'''

    def __init__(self):
        super(Collection, self).__init__()
        self.media = []
        self.metadata = []
        self.links = []

        self.importer = None

    def importFolder(self, folder):
        if self.importer is None:
                self.importer = Importer()
                self.connect(self.importer,   SIGNAL('importFinished'),  self.mergeCollection)
                self.connect(self.importer,   SIGNAL('progressChanged'),  self.progressChanged)

        self.importer.importFolder(folder)
        self.importer.start()

    def progressChanged(self,  tagged,  total):
        self.emit(SIGNAL('progressChanged'),  tagged,  total)

    def mergeCollection(self, result):
        #print 'Collection: Adding medias'

        coll = dict([(m.uniqueKey(), m) for m in self.media])
        merging_coll = dict([(m.uniqueKey(), m) for m in result.media])
        for k, v in merging_coll.items():
            if coll is not None and k in coll.keys():
                # TODO: have an update() method for medias
                pass
            else:
                self.media.append( v )

        coll = dict([(m.uniqueKey(), m) for m in self.metadata])
        merging_coll = dict([(m.uniqueKey(), m) for m in result.metadata])
        for k, v in merging_coll.items():
            if coll is not None and k in coll.keys():
                # TODO: rename merge() to update()
                coll[k].merge(v)
            else:
                self.metadata.append( v )

        if len(result.links) > 0:
            link_dict = dict([((a.uniqueKey(), b.uniqueKey()), (a, b)) for a, b in result.links])
            media_dict = dict([(m.uniqueKey(), m) for m in self.media])
            metadata_dict = dict([(m.uniqueKey(), m) for m in self.metadata])
            for (a_key, b_key), (a, b) in link_dict.items():
                new_link = (media_dict.get(a_key, a), metadata_dict.get(b_key, b))
                if new_link not in self.links:
                    self.links.append(new_link)

        self.emit(SIGNAL('collectionUpdated'))

    def filter(self, prop, value):
        result = Collection()
        for media, metadata in self.links:
            if metadata[prop] == value:
                if media not in result.media:
                    result.media += [ media ]

                if metadata not in result.metadata:
                    result.metadata += [ metadata ]

                result.links += [ (media, metadata) ]

        return result

    def __str__(self):
        return 'Collection:\nMedia = %s\nMetadata = %s' % (str(self.media), str(self.metadata))


    def load(self, filename):
        import cPickle

        try:
            f = open(filename)
        except:
            # if file is not found, just go on with an empty collection
            print 'WARNING: Collection', filename, 'does not exist'
            return

        self.media = cPickle.load(f)

        dicts = cPickle.load(f)
        self.metadata = [ Episode().fromDict(d) for d in dicts ]

        nlinks = cPickle.load(f)
        for (mn, mdn) in nlinks:
            self.links += [ (self.media[mn], self.metadata[mdn]) ]

    def save(self, filename):
        import cPickle
        f = open(filename, 'w')
        cPickle.dump(self.media, f)
        cPickle.dump([ m.toDict() for m in self.metadata ], f)

        # FIXME: cannot dump links correctly, need to use reference
        nlinks = []
        for (media, metadata) in self.links:
            nlinks += [ (self.media.index(media), self.metadata.index(metadata)) ]
        cPickle.dump(nlinks, f)

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
