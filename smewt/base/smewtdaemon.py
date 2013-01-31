#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2010 Nicolas Wack <wackou@smewt.com>
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

from PyQt4.QtCore import QSettings, QVariant, QTimer
from pygoo import MemoryObjectGraph, Equal, ontology
import smewt
from smewt import config
from smewt.media import Episode, Movie, Subtitle
from smewt.base import cache, utils, Collection, Media
from smewt.base.taskmanager import TaskManager, FuncTask
from os.path import join
from smewt.taggers import EpisodeTagger, MovieTagger
from smewt.plugins.amulefeedwatcher import AmuleFeedWatcher
import time, logging


log = logging.getLogger('smewt.base.smewtdaemon')


class VersionedMediaGraph(MemoryObjectGraph):

    def add_object(self, node, recurse = Equal.OnIdentity, excluded_deps = list()):
        result = super(VersionedMediaGraph, self).add_object(node, recurse, excluded_deps)
        if isinstance(result, Media):
            result.lastModified = time.time()

        return result

    def __getattr__(self, name):
        # if attr is not found and starts with an upper case letter, it might be the name
        # of one of the registered classes. In that case, return a function that would instantiate
        # such an object in this graph
        if name[0].isupper() and name in ontology.class_names():
            def inst(basenode = None, **kwargs):
                result = super(VersionedMediaGraph, self).__getattr__(name)(basenode, **kwargs)
                if isinstance(result, Media):
                    result.lastModified = time.time()
                return result

            return inst

        raise AttributeError, name



class SmewtDaemon(object):
    def __init__(self, progressCallback = None):
        super(SmewtDaemon, self).__init__()

        if smewt.config.PERSISTENT_CACHE:
            self.loadCache()

        # get a TaskManager for all the import tasks
        self.taskManager = TaskManager()
        self.taskManager.progressChanged.connect(self.progressChanged)

        # get our main graph DB
        self.loadDB()

        # get our collections: series and movies for now
        self.episodeCollection = Collection(name = 'Series',
                                            # import episodes and their subtitles too
                                            validFiles = [ Episode.isValidEpisode,
                                                           Subtitle.isValidSubtitle ],
                                            mediaTagger = EpisodeTagger,
                                            dataGraph = self.database,
                                            taskManager = self.taskManager)


        self.movieCollection = Collection(name = 'Movie',
                                          # import movies and their subtitles too
                                          validFiles = [ Movie.isValidMovie,
                                                         Subtitle.isValidSubtitle ],
                                          mediaTagger = MovieTagger,
                                          dataGraph = self.database,
                                          taskManager = self.taskManager)


        settings = QSettings()
        thumbs = settings.value('thumbnailsInitialized').toBool()

        if not thumbs:
            #self.regenerateSpeedDialThumbnails()
            settings.setValue('thumbnailsInitialized', True)
        else:
            pass
            # regenerate thumbnails once everything is setup, otherwise it seems somehow
            # we can't get the correct window size for taking the screenshot
            #if config.REGENERATE_THUMBNAILS:
            #    QTimer.singleShot(1000, self.regenerateSpeedDialThumbnails)

            # only start the update of the collections once our GUI is fully setup
            # do not rescan as it would be too long and we might delete some files that
            # are on an unaccessible network share or an external HDD
            #QTimer.singleShot(2000, self.updateCollections)
            self.taskManager.add(FuncTask('Update collections', self.updateCollections))

        # load up the feed watcher
        if config.PLUGIN_TVU:
            self.feedWatcher = AmuleFeedWatcher()

            # FIXME: this should go into a plugin.init() method

            # Make sure we have TVU's show list cached, as it takes quite some
            # time to download
            from smewt.plugins.tvudatasource import get_show_mapping
            from threading import Thread
            t = Thread(target=get_show_mapping)
            t.daemon = True
            t.start()


            # FIXME: this should go into a plugin.init() method
            from smewt.plugins import mldonkey
            mldonkey.send_command('vm')


            #from smewt.plugins import amulecommand
            #print '*'*100
            #amulecommand.recreateAmuleRemoteConf()


            #self.feedsTimer = QTimer(self)
            #self.connect(self.feedsTimer, SIGNAL('timeout()'),
            #             self.mainWidget.checkAllFeeds)
            #self.feedsTimer.start(2*60*60*1000)

    def quit(self):
        log.info('SmewtDaemon quitting...')
        self.taskManager.finishNow()
        self.saveDB()

        if smewt.config.PERSISTENT_CACHE:
            self.saveCache()

        log.info('SmewtDaemon quitting OK!')


    def progressChanged(self, current, total):
        if total == 0:
            self.saveDB()


    def loadCache(self):
        cache.load(utils.smewtUserPath(smewt.APP_NAME + '.cache'))

    def saveCache(self):
        cache.save(utils.smewtUserPath(smewt.APP_NAME + '.cache'))


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

    def clearDB(self):
        log.info('Clearing database...')
        self.database.clear()
        self.database.save(unicode(QSettings().value('database_file').toString()))


    def updateCollections(self):
        self.episodeCollection.update()
        self.movieCollection.update()

    def rescanCollections(self):
        self.episodeCollection.rescan()
        self.movieCollection.rescan()
