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

from smewt.taggers.tagger import Tagger
from smewt.guessers import *
from smewt.solvers import *
from PyQt4.QtCore import SIGNAL

from smewt import SmewtException, Graph, SolvingChain, Media, Metadata
from smewt.media import Episode, Series
import logging

log = logging.getLogger('smewt.taggers.episodetagger')

class EpisodeTagger(Tagger):
    def __init__(self):
        super(EpisodeTagger, self).__init__()

        self.chain1 = SolvingChain(EpisodeFilename(), MergeSolver(Episode))
        self.chain2 = SolvingChain(EpisodeIMDB(), SimpleSolver(Episode))

        # Connect the chains to our slots
        self.connect(self.chain1, SIGNAL('finished'), self.gotFilenameMetadata)
        self.connect(self.chain2, SIGNAL('finished'), self.solved)

    def gotFilenameMetadata(self, result):
        self.filenameMetadata = result.findOne(Episode)
        self.chain2.start(result)

    def solved(self, result):
        media = result.findOne(Media)
        log.debug('Finished tagging: %s', media)
        if not media.metadata:
            log.warning('Could not find any tag for: %s' % media)

            # we didn't find any info outside of what the filename told us
            media.metadata = self.filenameMetadata

            # try anyway to get the correct series name and poster
            from smewt.guessers.imdbmetadataprovider import IMDBMetadataProvider
            mdprovider = IMDBMetadataProvider()

            try:
                series = mdprovider.getSeries(media.metadata['series']['title'])
                result += media.metadata
                result.update(media.metadata, 'series', Series({ 'title': series }))
                result.update(media.metadata, 'episodeNumber', -1)

                lores, hires = mdprovider.getPoster(series.movieID)
                media.metadata['series']['loresImage'] = lores
                media.metadata['series']['hiresImage'] = hires

            except SmewtException:
                log.warning('Could not even find a probable series name for: %s' % media)


        self.emit(SIGNAL('tagFinished'), media)


    def tag(self, media):
        if media.type() in [ 'video', 'subtitle'] :
            if media.filename:
                query = Graph()
                query += media
                self.chain1.start(query)
                return
            else:
                log.warning('filename hasn\'t been set on Media object.')
        else:
            log.warning('Not a video media. Cannot tag. Filename = \'%s\'' % media.filename)

        # default tagger strategy if none other was applicable
        return super(EpisodeTagger, self).tag(media)
