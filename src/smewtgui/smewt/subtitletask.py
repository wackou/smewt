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
from smewt.taskmanager import Task
from smewt.media.series import Episode
from os.path import *
import logging

log = logging.getLogger('smewt.subtitletask')

class SubtitleTask(QThread, Task):
    def __init__(self, collection, episodes, language):
        super(SubtitleTask, self).__init__()
        self.totalCount = 0
        self.progressedCount = 0
        self.collection = collection
        self.episodes = episodes
        self.language = language

    def total(self):
        return self.totalCount

    def progressed(self):
        return self.progressedCount

    def run(self):
        self.worker = Worker(self.collection, self.episodes, self.language)

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
    def __init__(self, collection, episodes, language):
        super(Worker, self).__init__()

        self.collection = collection
        self.episodes = episodes
        self.language = language

    def begin(self):
        try:
            from smewt.media.subtitle import TVSubtitlesProvider
            tvsub = TVSubtitlesProvider()
        except:
            self.emit(SIGNAL('importFinished'), Graph())
            return
            
        languageMap = { 'en': u'English', 'fr': u'Français', 'sp': u'Spanish' }
        
        # find episodes which don't have subtitles and get it directly
        files = [ media for media in self.collection.nodes
                  if isinstance(media, Media) and media.metadata in self.episodes ]
        
        videos = [ f for f in files if f.type() == 'video' ]
        subtitles = [ f for f in files if f.type() == 'subtitle' ]

        subs = Graph()

        self.emit(SIGNAL('progressChanged'), 0, len(videos))
        
        for index, video in enumerate(videos):
            basename = splitext(video.filename)[0]
            subsBasename = basename + '.' + self.language
            foundSubs = [ s for s in subtitles if splitext(s.filename)[0] == subsBasename ]
            
            if foundSubs: continue
            
            episode = video.metadata
            log.info('MainWidget: trying to download subs for %s' % episode)
            subsFilename = tvsub.downloadSubtitle(subsBasename, episode['series']['title'],
                                                  episode['season'], episode['episodeNumber'], self.language,
                                                  video.filename)

            sub = Media( subsFilename )
            sub.metadata = episode
            
            self.emit(SIGNAL('progressChanged'), index + 1, len(videos))
            self.emit(SIGNAL('foundData'), sub)

            subs += sub

        self.emit(SIGNAL('progressChanged'), 0, 0)
        self.emit(SIGNAL('importFinished'), subs)
