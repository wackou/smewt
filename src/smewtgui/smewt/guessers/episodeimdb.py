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

from smewt import config
from smewt.guessers.guesser import Guesser
from smewt.media.series import Episode
from smewt.media.series.IMDBSerieMetadataFinder import IMDBSerieMetadataFinder

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode


class IMDBMetadataProvider(QObject):
    def __init__(self, metadata):
        super(IMDBMetadataProvider, self).__init__()

        if not metadata['serie']:
            raise SmewtException('IMDBMetadataProvider: Metadata doesn\'t contain \'serie\' field: %s', md)

        self.metadata = metadata
        self.imdb = IMDBSerieMetadataFinder()

    def start(self):
        name = self.metadata['serie']
        try:
            url = self.imdb.getSerieUrl(name)
            if not url:
                self.emit(SIGNAL('finished'), self.metadata, [])

            eps = self.imdb.getAllEpisodes(name, url)
            lores, hires = self.imdb.getSeriePoster(url)
            for ep in eps:
                ep['loresImage'] = lores
                ep['hiresImage'] = hires

            self.emit(SIGNAL('finished'), self.metadata, eps)

        except Exception, e:
            logging.warning(str(e))
            self.emit(SIGNAL('finished'), self.metadata, [])



class EpisodeIMDB(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(EpisodeIMDB, self).__init__()

    def start(self, query):
        self.checkValid(query)
        self.query = query

        found = query.metadata
        media = query.media[0]
        self.webparser = {}

        for md in list(found):
            if md['serie']:
                # little hack: if we have no season number, add 1 as default season number
                # (helps for series which have only 1 season)
                if not md['season']:
                    md['season'] = 1
                self.webparser[md] = IMDBMetadataProvider(md)
                self.connect(self.webparser[md], SIGNAL('finished'),
                             self.queryFinished)
            else:
                logging.warning('EpisodeIMDB: Metadata doesn\'t contain \'serie\' field: %s', md)

        for mdprovider in self.webparser.values():
            mdprovider.start()

    def queryFinished(self, metadata, guesses):
        del self.webparser[metadata]

        self.query.metadata += guesses

        if len(self.webparser) == 0:
            self.emit(SIGNAL('finished'), self.query)
