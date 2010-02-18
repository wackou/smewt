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

from __future__ import with_statement
from PyQt4.QtCore import SIGNAL, Qt, QObject, QThread
from smewt.base import Media, Task, SmewtException, textutils
from smewt.datamodel import MemoryObjectGraph
from smewt.media import Subtitle, SubtitleNotFoundError
import os.path

import itertools
import logging

log = logging.getLogger('smewt.subtitletask')

class SubtitleTask(QThread, Task):
    def __init__(self, collection, provider, title, language):
        super(SubtitleTask, self).__init__()
        self.collection = collection
        self.provider = provider
        validTitle = provider.titleFilter(title)
        self.objects = collection.findAll(validNode = lambda x: provider.canHandle(x) and validTitle(x))
        self.language = language

        log.info('Creating SubtitleTask for file: %s' % self.objects)


    def perform(self):
        languageMap = { 'en': u'English', 'fr': u'Fran\xe7ais', 'es': u'Espa\xf1ol' }

        # find objects which don't have yet a subtitle of the desired language
        currentSubs = self.collection.findAll(type = Subtitle,
                                              validNode = lambda x: x.metadata in self.objects,
                                              language = self.language)

        alreadyGood = set([ s['metadata'] for s in currentSubs ])

        videos = [ obj for obj in self.objects if obj not in alreadyGood ]
        if not videos:
            log.info('All videos already have subtitles')

        subs = MemoryObjectGraph()
        self.emit(SIGNAL('progressChanged'), 0, len(videos))

        index = 0
        for video in videos:
            try:
                videoFilename = self.collection.findOne(type = Media,
                                                        # the following assumes we always have a single metadata object for this file
                                                        select = lambda x: x.metadata == video).filename

                subFilename = os.path.splitext(videoFilename)[0] + '.%s.srt' % languageMap[self.language]

                # if file doesn't exist yet, try to download it
                if not os.path.isfile(subFilename):
                    possibleSubs = [ s for s in self.provider.getAvailableSubtitles(video) if s['language'] == self.language ]
                    if not possibleSubs:
                        raise SubtitleNotFoundError('didn\'t find any possible subs...')

                    # we could do a more elaborate selection here if more than 1 result is returned
                    candidate = possibleSubs[0]
                    if len(possibleSubs) > 1:
                        log.warning('More than 1 possible subtitle found: %s', str(possibleSubs))
                        dists = [ (textutils.levenshtein(videoFilename, sub['title']), sub) for sub in possibleSubs ]
                        sub = sorted(dists)[0][1]
                        log.warning('Choosing %s' % sub)

                    log.info('Trying to download subs for %s' % video)
                    subtext = self.provider.getSubtitle(candidate)

                    # write the subtitle in the appropriate file
                    # (here as well we might want to look at how many results we have (ie: movie
                    # spanning multiple CDs, etc...)
                    with open(subFilename, 'w') as f:
                        f.write(subtext)
                    log.info('Found subtitle for %s' % video)

                else:
                    log.warning('\'%s\' already exists. Not overwriting it...' % subFilename)

                # update the found subs with this one
                sub = Subtitle(metadata = video, language = self.language)
                subfile = Media(filename = subFilename, metadata = sub)

                subs += subfile

            except SubtitleNotFoundError, e:
                log.warning('subno: did not found any subtitle for %s: %s', str(video), str(e))

            except SmewtException, e:
                log.warning('se: did not found any subtitle for %s: %s' % (str(video), str(e)))

            self.emit(SIGNAL('progressChanged'), index + 1, len(videos))
            index += 1


        log.debug('SubtitleTask: all done!')
