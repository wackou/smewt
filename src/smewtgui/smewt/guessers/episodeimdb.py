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

from smewt import config, cachedmethod, utils, SmewtException, Graph, Media
from smewt.guessers.guesser import Guesser
from smewt.media.series import Episode, Series

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb


class IMDBMetadataProvider(QObject):
    def __init__(self, episode):
        super(IMDBMetadataProvider, self).__init__()

        if not episode['series']:
            raise SmewtException("IMDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)

        self.episode = episode
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
        # FIXME: find a better way to know whether there are episodes or not
        try:
            series['episodes']
        except:
            return []

        # TODO: debug to see if this is the correct way to access the series' title
        smewtSeries = Series({ 'title': series['title'] })
        for season in series['episodes']:
            for epNumber, episode in series['episodes'][season].items():
                ep = Episode({ 'series': smewtSeries })
                try:
                    ep['season'] = season
                    ep['episodeNumber'] = epNumber
                except:
                    # episode could not be entirely identified, what to do?
                    # can happen with 'unaired pilot', for instance, which has episodeNumber = 'unknown'
                    continue # just ignore this episode for now

                self.forwardData(ep, 'title', episode, 'title')
                self.forwardData(ep, 'synopsis', episode, 'plot')
                self.forwardData(ep, 'originalAirDate', episode, 'original air date')
                eps.append(ep)
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
        name = self.episode['series']['title']
        try:
            serie = self.getSerie(name)
            eps = self.getEpisodes(serie)
            lores, hires = self.getSeriesPoster(serie.movieID)
            if eps:
                eps[0]['series']['loresImage'] = lores
                eps[0]['series']['hiresImage'] = hires

            self.emit(SIGNAL('finished'), self.episode, eps)

        except Exception, e:
            logging.warning(str(e) + ' -- ' + str(ep))
            self.emit(SIGNAL('finished'), self.episode, [])



class EpisodeIMDB(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def start(self, query):
        self.checkValid(query)
        self.query = query

        logging.debug('EpisodeImdb: finding more info on %s' % query.findAll(Episode))
        ep = query.findOne(Episode)
        if ep['series']:
            # little hack: if we have no season number, add 1 as default season number
            # (helps for series which have only 1 season)
            if not ep['season']:
                query.update(ep, 'season', 1)

            self.mdprovider = IMDBMetadataProvider(ep)
            self.connect(self.mdprovider, SIGNAL('finished'),
                         self.queryFinished)
            self.mdprovider.start()

        else:
            logging.warning("EpisodeIMDB: Episode doesn't contain 'series' field: %s", ep)
            self.emit(SIGNAL('finished'), self.query)


    def queryFinished(self, ep, guesses):
        del self.mdprovider # why is that useful again?

        self.query += guesses

        self.emit(SIGNAL('finished'), self.query)
