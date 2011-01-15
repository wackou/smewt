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
from pygoo import MemoryObjectGraph
import smewt
from smewt.media import Series, Episode, Movie
from smewt.base import utils, Collection
from smewt.base.taskmanager import Task, TaskManager
from os.path import join, dirname, splitext, getsize
from smewt.taggers import EpisodeTagger, MovieTagger
import logging

log = logging.getLogger('smewt.base.smewtdaemon')

def episodeSizeFilter(filename):
    # episodes are videos < 600MB
    if utils.matchFile(filename, [ '*.avi',  '*.ogm',  '*.mkv' ]) and os.path.getsize(filename) < 600 * 1024 * 1024:
        return True
    return False


def movieSizeFilter(filename):
    # episodes are videos < 600MB
    if utils.matchFile(filename, [ '*.avi',  '*.ogm',  '*.mkv' ]) and os.path.getsize(filename) > 600 * 1024 * 1024:
        return True
    return False



def validEpisode(filename):
    return utils.matchFile(filename, ['*.avi', '*.ogm', '*.mkv']) and getsize(filename) < 600 * 1024 * 1024,

def validMovie(filename):
    return utils.matchFile(filename, ['*.avi', '*.ogm', '*.mkv']) and getsize(filename) > 600 * 1024 * 1024,


class SmewtDaemon(object):
    def __init__(self, progressCallback = None):
        super(SmewtDaemon, self).__init__()

        # FIXME: this is a lame hack to save the collection when we can...
        def callback(current, total):
            if total == 0:
                self.saveDB()
            if progressCallback is not None:
                progressCallback(current, total)

        self.taskManager = TaskManager(progressCallback = callback)

        # get our main graph DB
        self.loadDB()

        # get our collections: series and movies for now
        self.episodeCollection = Collection(name = 'Series',
                                           # episodes are videos < 600MB and/or subtitles
                                           validFiles = [ validEpisode, '*.sub', '*.srt' ],
                                           mediaTagger = EpisodeTagger,
                                           dataGraph = self.database,
                                           taskManager = self.taskManager)


        self.movieCollection = Collection(name = 'Movie',
                                          # movies are videos > 600MB and/or subtitles
                                          validFiles = [ validMovie, '*.sub', '*.srt' ],
                                          mediaTagger = MovieTagger,
                                          dataGraph = self.database,
                                          taskManager = self.taskManager)


        # update them when we start the daemon; do not rescan as it would be too long
        # and we might delete some files that are on an unaccessible network share or
        # an external HDD
        self.updateCollections()


    def loadDB(self):
        log.info('Loading database...')
        settings = QSettings()
        dbfile = unicode(settings.value('database_file').toString())
        if not dbfile:
            dbfile = join(utils.smewtUserDirectory(), smewt.APP_NAME + '.database')
            settings.setValue('database_file', QVariant(dbfile))

        self.database = MemoryObjectGraph()
        try:
            self.database.load(dbfile)
        except:
            log.warning('Could not load database %s', dbfile)

    def saveDB(self):
        log.info('Saving database...')
        self.database.save(unicode(QSettings().value('database_file').toString()))

    def shutdown(self):
        log.info('SmewtDaemon shutdown')
        self.saveDB()

    def quit(self):
        log.info('SmewtDaemon quit')
        self.taskManager.abortAll()

    def updateCollections(self):
        self.episodeCollection.update()
        self.movieCollection.update()

    def rescanCollections(self):
        self.episodeCollection.rescan()
        self.movieCollection.rescan()

