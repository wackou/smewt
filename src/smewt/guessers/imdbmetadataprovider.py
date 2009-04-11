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

from smewt import cachedmethod, utils, SmewtException, Graph, Media
from smewt.guessers.guesser import Guesser
from smewt.media import Episode, Series, Movie
from smewt.base import textutils

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb

log = logging.getLogger('smewt.guessers.imdbmetadataprovider')


class Getter:
    def __init__(self, md, d):
        self.md = md
        self.d = d

    def get(self, name, fromName = None):
        if not fromName:
            fromName = name
        try:
            self.md[name] = self.d[fromName]
        except KeyError:
            pass

    def getMultiUnicode(self, name):
        try:
            self.md[name] = [ unicode(s) for s in self.d[name] ]
        except KeyError:
            pass


class IMDBMetadataProvider(QObject):
    def __init__(self):
        super(IMDBMetadataProvider, self).__init__()

        self.imdb = imdb.IMDb()

    @cachedmethod
    def getSeries(self, name):
        results = self.imdb.search_movie(name)
        for r in results:
            if r['kind'] == 'tv series' or r['kind'] == 'tv mini series':
                return r
        raise SmewtException("EpisodeIMDB: Could not find series '%s'" % name)


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

                g = Getter(ep, episode)
                g.get('title')
                g.get('synopsis', 'plot')
                g.get('originalAirDate', 'original air date')

                eps.append(ep)

        return eps

    @cachedmethod
    def getMovie(self, name):
        log.debug('MovieIMDB: looking for movie %s', name)
        results = self.imdb.search_movie(name)
        for r in results:
            if r['kind'] == 'movie' or r['kind'] == 'video movie':
                return r
        raise SmewtException("MovieIMDB: Could not find movie '%s'" % name)

    @cachedmethod
    def getMovieData(self, movieImdb):
        self.imdb.update(movieImdb)
        movie = Movie({ 'title': movieImdb['title'],
                        'year': movieImdb['year']
                        })
        g = Getter(movie, movieImdb)
        g.get('rating')
        g.get('plot')
        g.get('plotOutline', 'plot outline')
        g.getMultiUnicode('writer') # documentaries don't have writers...
        g.getMultiUnicode('director')
        g.getMultiUnicode('genres')

        try:
            movie['cast'] = [ (unicode(p), unicode(p.currentRole)) for p in movieImdb['cast'][:15] ]
        except:
            movie['cast'] = []

        return movie


    @cachedmethod
    def getPoster(self, imdbID):
        # FIXME: big hack!
        import os
        from os.path import join
        imageDir = join(os.getcwd(), 'smewt', 'media', 'common', 'images')
        os.system('mkdir -p "%s"' % imageDir)

        loresFilename, hiresFilename = None, None

        try:
            movieUrl = 'http://www.imdb.com/title/tt' + imdbID
            html = urlopen(movieUrl).read()
            rexp = '<a name="poster" href="(?P<hiresUrl>[^"]*)".*?src="(?P<loresImg>[^"]*)"'
            poster = textutils.matchRegexp(html, rexp)
            loresFilename = imageDir + '/%s_lores.jpg' % imdbID
            open(loresFilename, 'w').write(urlopen(poster['loresImg']).read())
        except Exception, e:
            loresFilename = join(os.getcwd(), 'smewt', 'media', 'common', 'images', 'noposter.png')
            log.warning('Could not find lores poster for imdb ID %s because: %s' % (imdbID, str(e)[:100]))

        try:
            html = urlopen('http://www.imdb.com' + poster['hiresUrl']).read()
            rexp = '<table id="principal">.*?src="(?P<hiresImg>[^"]*)"'
            poster = textutils.matchRegexp(html, rexp)
            hiresFilename = imageDir + '/%s_hires.jpg' % imdbID
            open(hiresFilename, 'w').write(urlopen(poster['hiresImg']).read())
        except Exception, e:
            hiresFilename = join(os.getcwd(), 'smewt', 'media', 'common', 'images', 'noposter.png')
            log.warning('Could not find hires poster for imdb ID %s because: %s' % (imdbID, str(e)[:100]))


        return (loresFilename, hiresFilename)


    def startEpisode(self, episode):
        if not episode['series']:
            raise SmewtException("IMDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)

        name = episode['series']['title']
        try:
            series = self.getSeries(name)
            eps = self.getEpisodes(series)
            lores, hires = self.getPoster(series.movieID)
            if eps:
                eps[0]['series']['loresImage'] = lores
                eps[0]['series']['hiresImage'] = hires

            self.emit(SIGNAL('finished'), episode, eps)

        except Exception, e:
            log.warning(str(e) + ' -- ' + textutils.toUtf8(episode))
            self.emit(SIGNAL('finished'), episode, [])

    def startMovie(self, movieName):
        try:
            movieImdb = self.getMovie(movieName)
            movie = self.getMovieData(movieImdb)
            lores, hires = self.getPoster(movieImdb.movieID)
            movie['loresImage'] = lores
            movie['hiresImage'] = hires

            self.emit(SIGNAL('finished'), movie)

        except Exception, e:
            log.warning(str(e) + ' -- ' + textutils.toUtf8(movieName))
            self.emit(SIGNAL('finished'), movieName, [])

