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

from smewt.base import GraphAction, Media, Metadata, SmewtException
from smewt.base.utils import guessitToPygoo
from smewt.base.mediaobject import foundMetadata
from smewt.media import Episode, Series
from guessit import guess_episode_info
import logging

log = logging.getLogger('smewt.guessers.episodefilename')


class EpisodeFilename(GraphAction):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(EpisodeFilename, self).__init__()

    def canHandle(self, query):
        if query.find_one(Media).type() not in [ 'video', 'subtitle' ]:
            raise SmewtException("%s: can only handle video or subtitle media objects" % self.__class__.__name__)

    def perform(self, query):
        self.checkValid(query)

        media = query.find_one(Media)

        episodeMetadata = guess_episode_info(media.filename)
        episodeMetadata = guessitToPygoo(episodeMetadata)

        averageConfidence = sum(episodeMetadata.confidence(prop) for prop in episodeMetadata) / len(episodeMetadata)

        # put the result of guessit in a form that smewt understands
        series = query.Series(title = episodeMetadata.pop('series'))
        episode = query.Episode(allow_incomplete = True, confidence = averageConfidence, series = series, **episodeMetadata)

        result = foundMetadata(query, episode)
        #result.display_graph()

        return result
