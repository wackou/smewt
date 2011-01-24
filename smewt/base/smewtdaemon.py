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
from pygoo import MemoryObjectGraph, Equal
import smewt
from smewt.media import Series, Episode, Movie
from smewt.base import utils, Collection, Media
from smewt.base.taskmanager import Task, TaskManager
from os.path import join, dirname, splitext, getsize
from smewt.taggers import EpisodeTagger, MovieTagger
import time, logging

log = logging.getLogger('smewt.base.smewtdaemon')


class VersionedMediaGraph(MemoryObjectGraph):

    def add_object(self, node, recurse = Equal.OnIdentity, excluded_deps = list()):
        result = super(VersionedMediaGraph, self).add_object(node, recurse, excluded_deps)
        if isinstance(result, Media):
            result.lastModified = time.time()

        return result


def validEpisode(filename):
    return utils.matchFile(filename, [ '*.avi', '*.ogm', '*.mkv' ]) #and getsize(filename) < 600 * 1024 * 1024

def validMovie(filename):
    return utils.matchFile(filename, [ '*.avi', '*.ogm', '*.mkv' ]) #and getsize(filename) > 600 * 1024 * 1024


class SmewtDaemon(object):
    def __init__(self, progressCallback = None):
        super(SmewtDaemon, self).__init__()

        # get a TaskManager for all the import tasks
        self.taskManager = TaskManager()
        self.taskManager.progressChanged.connect(self.progressChanged)

        # get our main graph DB
        self.loadDB()

        # get our collections: series and movies for now
        self.episodeCollection = Collection(name = 'Series',
                                           # episodes are videos < 600MB and/or subtitles
                                           validFiles = [ validEpisode, '*.idx', '*.sub', '*.srt' ],
                                           mediaTagger = EpisodeTagger,
                                           dataGraph = self.database,
                                           taskManager = self.taskManager)


        self.movieCollection = Collection(name = 'Movie',
                                          # movies are videos > 600MB and/or subtitles
                                          validFiles = [ validMovie, '*.idx', '*.sub', '*.srt' ],
                                          mediaTagger = MovieTagger,
                                          dataGraph = self.database,
                                          taskManager = self.taskManager)



    def progressChanged(self, current, total):
        if total == 0:
            self.saveDB()


    def loadDB(self):
        log.info('Loading database...')
        settings = QSettings()
        dbfile = unicode(settings.value('database_file').toString())
        if not dbfile:
            dbfile = join(utils.smewtUserDirectory(), smewt.APP_NAME + '.database')
            settings.setValue('database_file', QVariant(dbfile))

        self.database = VersionedMediaGraph()
        try:
            self.database.load(dbfile)
        except:
            log.warning('Could not load database %s', dbfile)

    def saveDB(self):
        log.info('Saving database...')
        self.database.save(unicode(QSettings().value('database_file').toString()))

    def quit(self):
        log.info('SmewtDaemon quitting...')
        self.taskManager.finishNow()
        self.saveDB()
        log.info('SmewtDaemon quitting OK!')

    def updateCollections(self):
        self.episodeCollection.update()
        self.movieCollection.update()

    def rescanCollections(self):
        self.episodeCollection.rescan()
        self.movieCollection.rescan()

