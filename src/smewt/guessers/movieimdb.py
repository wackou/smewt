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

from smewt.base import cachedmethod, utils, SmewtException, Media
from smewt.guessers.guesser import Guesser
from smewt.media import Movie

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb
from smewt.base import textutils
from imdbmetadataprovider import IMDBMetadataProvider

log = logging.getLogger('smewt.guessers.movieimdb')

class MovieIMDB(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def start(self, query):
        self.checkValid(query)
        self.query = query

        #query.displayGraph()

        log.debug('MovieImdb: finding more info on %s' % query.findAll(type = Media))
        movie = query.findOne(type = Movie)
        # if valid movie

        self.mdprovider = IMDBMetadataProvider()
        self.connect(self.mdprovider, SIGNAL('finished'),
                     self.queryFinished)

        self.mdprovider.startMovie(movie.title)

    def queryFinished(self, guess):
        del self.mdprovider # why is that useful again?

        media = self.query.findOne(type = Media)
        print 'guess', guess
        media.metadata = guess
        result = MemoryObjectGraph()
        result += media

        self.emit(SIGNAL('finished'), result)
