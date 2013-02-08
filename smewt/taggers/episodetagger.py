#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
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

from __future__ import unicode_literals
from smewt.base import SolvingChain, Media, utils
from smewt.base.textutils import u
from smewt.media import Episode
from smewt.taggers.tagger import Tagger
from smewt.guessers import EpisodeFilename, EpisodeTVDB
from smewt.solvers import SimpleSolver
import logging

log = logging.getLogger(__name__)

class EpisodeTagger(Tagger):

    def perform(self, query):
        log.info('EpisodeTagger tagging episode: %s' % u(query.find_one(Media).filename))
        filenameMetadata = SolvingChain(EpisodeFilename()).solve(query)

        log.info('EpisodeTagger found info: %s' % filenameMetadata.find_one(Episode))
        result = SolvingChain(EpisodeTVDB(), SimpleSolver(Episode)).solve(filenameMetadata)

        media = result.find_one(Media)

        # if we didn't find a valid episode but we still have a series, let's create a syntactically
        # valid episode anyway so it can be imported
        if not media.metadata.get('episodeNumber'):
            media.metadata.episodeNumber = -1

        # import subtitles correctly
        if media.type() == 'subtitle':
            subs = []
            for language in utils.guessCountryCodes(media.filename):
                log.info('Found %s sub in file %s' % (language.english_name, u(media.filename)))
                subs += [ result.Subtitle(metadata = media.metadata,
                                          language = language.alpha2) ]

            media.metadata = subs


        self.cleanup(result)

        log.debug('Finished tagging: %s' % media.filename)
        return result
