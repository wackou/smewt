#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
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

from smewt.base import Media, utils
from smewt.taggers.tagger import Tagger
from smewt.guessers import *
import logging

log = logging.getLogger('smewt.taggers.movietagger')

class MovieTagger(Tagger):
    def perform(self, query):
        filenameMetadata = MovieFilename().perform(query)
        result = MovieTMDB().perform(filenameMetadata)

        media = result.find_one(Media)
        if not media.metadata:
            log.warning('Could not find any tag for: %s' % media)


        # import subtitles correctly
        if media.type() == 'subtitle':
            # FIXME: problem for vobsubs: as a media points to a single metadata object, we cannot
            # represent a .sub for 3 different languages...
            subs = []
            for language in utils.guessCountryCode(media.filename):
                subs += [ result.Subtitle(metadata = media.metadata,
                                          language = language) ]

                media.metadata = subs


        self.cleanup(result)
        log.debug('Finished tagging: %s' % media)

        return result
