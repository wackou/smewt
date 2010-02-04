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
from smewt.media.series import Episode, Series
from smewt.base.mediaobject import foundMetadata
from smewt.datamodel import Equal

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb
from imdbmetadataprovider import IMDBMetadataProvider


log = logging.getLogger('smewt.guessers.episodeimdb')


class EpisodeIMDB(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def start(self, query):
        self.checkValid(query)
        self.query = query

        log.debug('EpisodeImdb: finding more info on %s' % query.findAll(type = Episode))
        ep = query.findOne(type = Episode)

        if ep.get('series') is None:
            log.warning("EpisodeIMDB: Episode doesn't contain 'series' field: %s", ep)
            self.emit(SIGNAL('finished'), self.query)
            return

        # little hack: if we have no season number, add 1 as default season number
        # (helps for series which have only 1 season)
        if ep.get('season') is None:
            ep.season = 1

        self.mdprovider = IMDBMetadataProvider()
        self.connect(self.mdprovider, SIGNAL('finished'),
                     self.queryFinished)

        self.mdprovider.startEpisode(ep)


    def queryFinished(self, ep, guesses):
        del self.mdprovider # why is that useful again?

        result = self.query
        for ep in guesses.findAll(Episode):
            result.addObject(ep, recurse = Equal.OnLiterals)

        #result.displayGraph()
        self.emit(SIGNAL('finished'), result)
