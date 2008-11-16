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

from smewt import config, cachedmethod, utils
from smewt.guessers.guesser import Guesser
from smewt.media.series import Episode

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb


class IMDBMetadataProvider(QObject):
    def __init__(self, metadata):
        super(IMDBMetadataProvider, self).__init__()

        if not metadata['series']:
            raise SmewtException("IMDBMetadataProvider: Metadata doesn't contain 'series' field: %s", md)

        self.metadata = metadata
        self.imdb = imdb.IMDb()

    @cachedmethod
    def getSerie(self, name):
        results = self.imdb.search_movie(name)
        for r in results:
            if r['kind'] == 'tv series':
                return r
        raise SmewtException("EpisodeIMDB: Could not find series '%s'" % name)

    def forwardData(self, d, dname, ep, epname):
        try:
            d[dname] = ep[epname]
        except: pass

    @cachedmethod
    def getEpisodes(self, series):
        self.imdb.update(series, 'episodes')
        eps = []
        for season in series['episodes']:
            for epNumber, episode in series['episodes'][season].items():
                ep = {}
                ep['season'] = season
                ep['episodeNumber'] = epNumber
                self.forwardData(ep, 'title', episode, 'title')
                self.forwardData(ep, 'synopsis', episode, 'plot')
                self.forwardData(ep, 'series', episode, 'series title')
                self.forwardData(ep, 'originalAirDate', episode, 'original air date')
                eps.append(Episode().fromDict(ep))
        return eps

    @cachedmethod
    def getSeriesPoster(self, seriesID):
        # FIXME: big hack!
        import os
        imageDir = os.getcwd()+'/smewt/media/series/images'
        os.system('mkdir -p "%s"' % imageDir)

        loresFilename, hiresFilename = None, None

        try:
            serieUrl = 'http://www.imdb.com/title/tt' + seriesID
            html = urlopen(serieUrl).read()
            rexp = '<a name="poster" href="(?P<hiresUrl>[^"]*)".*?src="(?P<loresImg>[^"]*)"'
            poster = utils.matchRegexp(html, rexp)
            loresFilename = imageDir + '/%s_lores.jpg' % seriesID
            open(loresFilename, 'w').write(urlopen(poster['loresImg']).read())
        except:
            pass

        try:
            html = urlopen('http://www.imdb.com' + poster['hiresUrl']).read()
            rexp = '<table id="principal">.*?src="(?P<hiresImg>[^"]*)"'
            poster = utils.matchRegexp(html, rexp)
            hiresFilename = imageDir + '/%s_hires.jpg' % seriesID
            open(hiresFilename, 'w').write(urlopen(poster['hiresImg']).read())
        except:
            pass

        return (loresFilename, hiresFilename)


    def start(self):
        name = self.metadata['series']
        try:
            serie = self.getSerie(name)
            eps = self.getEpisodes(serie)
            lores, hires = self.getSeriesPoster(serie.movieID)
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
            if md['series']:
                # little hack: if we have no season number, add 1 as default season number
                # (helps for series which have only 1 season)
                if not md['season']:
                    md['season'] = 1
                self.webparser[md] = IMDBMetadataProvider(md)
                self.connect(self.webparser[md], SIGNAL('finished'),
                             self.queryFinished)
            else:
                logging.warning("EpisodeIMDB: Metadata doesn't contain 'series' field: %s", md)

        for mdprovider in self.webparser.values():
            mdprovider.start()

    def queryFinished(self, metadata, guesses):
        del self.webparser[metadata]

        self.query.metadata += guesses

        if len(self.webparser) == 0:
            self.emit(SIGNAL('finished'), self.query)
