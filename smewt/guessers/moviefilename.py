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

from smewt.base import GraphAction, SmewtException
from smewt.ontology import Media, foundMetadata
from smewt.base.utils import tolist, guessitToPygoo
from guessit import guess_movie_info
import logging

log = logging.getLogger(__name__)


class MovieFilename(GraphAction):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(MovieFilename, self).__init__()

    def canHandle(self, query):
        media = query.find_one(Media)
        if media.type() not in ('video', 'subtitle'):
            raise SmewtException("%s: can only handle video or subtitle media objects: %s" % (self.__class__.__name__, media.filename))

    def perform(self, query):
        self.checkValid(query)
        media = query.find_one(node_type = Media)

        movieMetadata = guess_movie_info(media.filename)
        movieMetadata = guessitToPygoo(movieMetadata)

        # FIXME: this is a temporary hack waiting for the pygoo and ontology refactoring
        if len(tolist(movieMetadata.get('language', None))) > 1:
            movieMetadata['language'] = movieMetadata['language'][0]


        averageConfidence = sum(movieMetadata.confidence(prop) for prop in movieMetadata) / len(movieMetadata)

        # put the result of guessit in a form that smewt understands
        movie = query.Movie(confidence = averageConfidence, **movieMetadata)

        msg = u'Found filename information from %s:' % media.filename
        msg += str(movie).decode('utf-8')
        log.debug(msg)

        result = foundMetadata(query, movie)
        #result.display_graph()

        return result
