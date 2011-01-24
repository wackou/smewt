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

from smewt.base import GraphAction, cachedmethod, utils, textutils, SmewtException, Media
from smewt.base.utils import smewtDirectory
from smewt.base.textutils import toUtf8
from smewt.base.mediaobject import foundMetadata
from smewt.guessers.guesser import Guesser
from smewt.media import Movie
from pygoo import MemoryObjectGraph
from urllib import urlopen,  urlencode
from tvdbmetadataprovider import TVDBMetadataProvider
import logging

log = logging.getLogger('smewt.guessers.movietmdb')

class MovieTMDB(GraphAction):

    supportedTypes = [ 'video', 'subtitle' ]

    def canHandle(self, query):
        return True

    def perform(self, query):
        self.checkValid(query)

        log.debug('MovieTvdb: finding more info on %s' % query.find_one(Movie))
        movie = query.find_one(Movie)

        try:
            mdprovider = TVDBMetadataProvider()
            result = mdprovider.startMovie(movie.title)
        except SmewtException, e:
            # movie could not be found, return a dummy Unknown movie instead so we can group them somewhere
            log.warning('Could not find info for movie: %s' % toUtf8(query.find_one(Media).filename))
            noposter = smewtDirectory('smewt', 'media', 'common', 'images', 'noposter.png')
            result = MemoryObjectGraph()
            result.Movie(title = 'Unknown', loresImage = noposter, hiresImage = noposter)

        result = foundMetadata(query, result.find_one(Movie))
        return result

