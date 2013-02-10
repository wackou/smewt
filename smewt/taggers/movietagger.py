#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
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
from smewt.base import utils
from smewt.base.textutils import u
from smewt.ontology import Media, Movie
from smewt.taggers.tagger import Tagger
from smewt.guessers import MovieFilename, MovieTMDB
import logging

log = logging.getLogger(__name__)

class MovieTagger(Tagger):
    def perform(self, query):
        filename = u(query.find_one(Media).filename)
        log.info('MovieTagger tagging movie: %s' % filename)
        filenameMetadata = MovieFilename().perform(query)
        filenameMovie = filenameMetadata.find_one(Movie)
        log.info('MovieTagger found info: %s' % u(filenameMovie))
        result = MovieTMDB().perform(filenameMetadata)

        media = result.find_one(Media)
        if not media.metadata:
            log.warning('Could not find any tag for: %s' % media)

        # import the info we got from the filename if nothing better came in with MovieTMDB
        for prop in filenameMovie.keys():
            if prop not in media.metadata and prop not in media:
                media[prop] = filenameMovie[prop]

        # import subtitles correctly
        if media.type() == 'subtitle':
            # FIXME: problem for vobsubs: as a media points to a single metadata object, we cannot
            # represent a .sub for 3 different languages...
            subs = []
            for language in utils.guessCountryCodes(media.filename):
                subs += [ result.Subtitle(metadata = media.metadata,
                                          language = language.alpha2) ]

            media.metadata = subs


        self.cleanup(result)

        log.debug('Finished tagging: %s' % u(media))
        return result
