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

from smewt.base import SmewtException, SolvingChain, Media, Metadata, utils
from smewt.base.textutils import toUtf8
from smewt.media import Episode, Series, Subtitle
from smewt.taggers.tagger import Tagger
from smewt.guessers import *
from smewt.solvers import *
from pygoo import MemoryObjectGraph
import logging

log = logging.getLogger('smewt.taggers.episodetagger')

class EpisodeTagger(Tagger):

    def perform(self, query):
        log.info('EpisodeTagger tagging episode: %s' % toUtf8(query.find_one(Media).filename))
        filenameMetadata = SolvingChain(EpisodeFilename(), MergeSolver(Episode)).solve(query)
        log.info('EpisodeTagger found info from filename: %s' % filenameMetadata.find_one(Episode))
        result = SolvingChain(EpisodeTVDB(), SimpleSolver(Episode)).solve(filenameMetadata)

        media = result.find_one(Media)

        # if we didn't find a valid episode but we still have a series, let's create a syntactically
        # valid episode anyway so it can be imported
        if not media.metadata.get('episodeNumber'):
            media.metadata.episodeNumber = -1

        # import subtitles correctly
        if media.type() == 'subtitle':
            subs = []
            for language in utils.guessCountryCode(media.filename):
                log.info('Found %s sub in file %s' % (toUtf8(language), toUtf8(media.filename)))
                subs += [ result.Subtitle(metadata = media.metadata,
                                          language = language) ]

            media.metadata = subs


        self.cleanup(result)

        log.debug('Finished tagging: %s' % media.filename)
        return result
