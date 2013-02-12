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

from pygoo import MemoryObjectGraph, Equal, ontology
from guessit.slogging import setupLogging
from smewt import config
from smewt.ontology import Episode, Movie, Subtitle, Media, Config
from smewt.base import cache, utils, Collection
from smewt.base.taskmanager import TaskManager, FuncTask
from smewt.taggers import EpisodeTagger, MovieTagger
from smewt.plugins.feedwatcher import FeedWatcher
from threading import Timer
from os.path import join
import smewt
import time
import os
import logging

log = logging.getLogger(__name__)


class VersionedMediaGraph(MemoryObjectGraph):

    def __init__(self, *args, **kwargs):
        super(VersionedMediaGraph, self).__init__(*args, **kwargs)


    def add_object(self, node, recurse = Equal.OnIdentity, excluded_deps = list()):
        result = super(VersionedMediaGraph, self).add_object(node, recurse, excluded_deps)
        if isinstance(result, Media):
            result.lastModified = time.time()

        return result

    def clear(self):
        # we want to keep our config object untouched
        tmp = MemoryObjectGraph()
        tmp.add_object(self.config)
        super(VersionedMediaGraph, self).clear()
        self.add_object(tmp.find_one(Config))

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


    @property
    def config(self):
        try:
            return self.find_one(Config)
        except ValueError:
            return self.Config()


class SmewtDaemon(object):
    def __init__(self):
        super(SmewtDaemon, self).__init__()

        # Note: put log file in data dir instead of log dir so that it is
        #       accessible through the user/ folder static view
        self.logfile = utils.path(smewt.dirs.user_data_dir, 'Smewt.log')
        setupLogging(filename=self.logfile, with_time=True, with_thread=True)


        if smewt.config.PERSISTENT_CACHE:
            self.loadCache()

        # get a TaskManager for all the import tasks
        self.taskManager = TaskManager()

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


        if config.REGENERATE_THUMBNAILS:
            # launch the regeneration of the thumbnails, but only after everything
            # is setup and we are able to serve requests
            Timer(3, self.regenerateSpeedDialThumbnails).start()


        # load up the feed watcher
        if config.PLUGIN_TVU:
            self.feedWatcher = FeedWatcher(self)

        if config.PLUGIN_MLDONKEY:
            # FIXME: this should go into a plugin.init() method
            from smewt.plugins import mldonkey
            mldonkey.send_command('vm')

        # do not rescan as it would be too long and we might delete some files that
        # are on an unaccessible network share or an external HDD
        self.taskManager.add(FuncTask('Update collections', self.updateCollections))



    def quit(self):
        log.info('SmewtDaemon quitting...')
        self.taskManager.finishNow()
        if config.PLUGIN_TVU:
            self.feedWatcher.quit()
        self.saveDB()

        if smewt.config.PERSISTENT_CACHE:
            self.saveCache()

        log.info('SmewtDaemon quitting OK!')


    def _cacheFilename(self):
        return utils.path(smewt.dirs.user_cache_dir,
                          smewt.APP_NAME + '.cache',
                          createdir=True)

    def loadCache(self):
        cache.load(self._cacheFilename())

    def saveCache(self):
        cache.save(self._cacheFilename())

    def clearCache(self):
        cache.clear()
        cacheFile = self._cacheFilename()
        log.info('Deleting cache file: %s' % cacheFile)
        try:
            os.remove(cacheFile)
        except OSError:
            pass


    def loadDB(self):
        dbfile = smewt.settings.get('database_file')
        if not dbfile:
            dbfile = join(utils.smewtUserDirectory(), smewt.APP_NAME + '.database')
            smewt.settings.set('database_file', dbfile)

        log.info('Loading database from: %s', dbfile)
        self.database = VersionedMediaGraph()
        try:
            self.database.load(dbfile)
        except:
            log.warning('Could not load database %s', dbfile)

    def saveDB(self):
        dbfile = smewt.settings.get('database_file')
        log.info('Saving database to %s', dbfile)
        self.database.save(dbfile)

    def clearDB(self):
        log.info('Clearing database...')
        self.database.clear()
        self.database.save(smewt.settings.get('database_file'))


    def updateCollections(self):
        self.episodeCollection.update()
        self.movieCollection.update()

    def rescanCollections(self):
        self.episodeCollection.rescan()
        self.movieCollection.rescan()


    def _regenerateSpeedDialThumbnails(self):
        import shlex, subprocess
        from PIL import Image
        from StringIO import StringIO
        webkit2png = (subprocess.call(['which', 'webkit2png'], stdout=subprocess.PIPE) == 0)
        if not webkit2png:
            log.warning('webkit2png not found. please run: pip install git+https://github.com/adamn/python-webkit2png.git@6488a1fbd06d5479f8592af47acc73834647e837')
            return

        def gen(path, filename):
            width, height = 200, 150
            log.info('Creating %dx%d screenshot for %s...' % (width, height, path))
            filename = utils.path(smewt.dirs.user_data_dir, 'speeddial', filename)
            cmd = 'webkit2png -g 1000 600 "http://localhost:6543%s"' % path
            screenshot, _ = subprocess.Popen(shlex.split(cmd),
                                             stdout=subprocess.PIPE).communicate()
            im = Image.open(StringIO(screenshot))
            im.thumbnail((width, height), Image.ANTIALIAS)
            im.save(filename, "PNG")

        gen('/movies', 'allmovies.png')
        gen('/movies/table', 'moviestable.png')
        gen('/movies/recent', 'recentmovies.png')
        gen('/series', 'allseries.png')
        gen('/series/suggestions', 'episodesuggestions.png')

    def regenerateSpeedDialThumbnails(self):
        self.taskManager.add(FuncTask('Regenerate thumbnails',
                                      self._regenerateSpeedDialThumbnails))
