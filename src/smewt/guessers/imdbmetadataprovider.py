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
from smewt.media import Episode, Series, Movie
from smewt.base import textutils
from smewt.base.utils import smewtDirectory, smewtUserDirectory
from pygoo import MemoryObjectGraph

from PyQt4.QtCore import SIGNAL, QObject, QUrl

import os, sys, re, logging
from urllib import urlopen,  urlencode
from smewt.base.utils import curlget
from lxml import etree
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
            self.md.set(name, self.d[fromName])
        except KeyError:
            pass

    def getMultiUnicode(self, name):
        try:
            self.md.set(name, [ unicode(s) for s in self.d[name] ])
        except KeyError:
            pass


class IMDBMetadataProvider(object):
    def __init__(self):
        super(IMDBMetadataProvider, self).__init__()

        self.imdb = imdb.IMDb()

    @cachedmethod
    def getSeries(self, name):
        """Get the IMDBPy series object given its name."""
        results = self.imdb.search_movie(name)
        for r in results:
            if r['kind'] == 'tv series' or r['kind'] == 'tv mini series':
                return r
        raise SmewtException("EpisodeIMDB: Could not find series '%s'" % name)


    @cachedmethod
    def getEpisodes(self, series):
        """From a given IMDBPy series object, return a graph containing its information
        as well as its episodes nodes."""
        self.imdb.update(series, 'episodes')

        # TODO: debug to see if this is the correct way to access the series' title
        result = MemoryObjectGraph()
        smewtSeries = result.Series(title = series['title'])

        # FIXME: find a better way to know whether there are episodes or not
        try:
            series['episodes']
        except:
            return result

        for season in series['episodes']:
            for epNumber, episode in series['episodes'][season].items():
                try:
                    ep = result.Episode(series = smewtSeries,
                                        season = season,
                                        episodeNumber = epNumber)
                except:
                    # episode could not be entirely identified, what to do?
                    # can happen with 'unaired pilot', for instance, which has episodeNumber = 'unknown'
                    log.warning('invalid season/epnumber pair: %s / %s' % (season, epNumber))
                    continue # just ignore this episode for now

                g = Getter(ep, episode)
                g.get('title')
                g.get('synopsis', 'plot')
                g.get('originalAirDate', 'original air date')

        return result

    @cachedmethod
    def getMovie(self, name):
        """Get the IMDBPy movie object given its name."""
        log.debug('MovieIMDB: looking for movie %s', name)
        results = self.imdb.search_movie(name)
        for r in results:
            if r['kind'] == 'movie' or r['kind'] == 'video movie':
                return r
        raise SmewtException("MovieIMDB: Could not find movie '%s'" % name)

    @cachedmethod
    def getMovieData(self, movieImdb):
        """From a given IMDBPy movie object, return a graph containing its information."""
        self.imdb.update(movieImdb)
        result = MemoryObjectGraph()
        movie = result.Movie(title = movieImdb['title'],
                             year = movieImdb['year'])

        g = Getter(movie, movieImdb)
        g.get('rating')
        g.get('plot')
        g.get('plotOutline', 'plot outline')
        g.getMultiUnicode('writer') # documentaries don't have writers...
        g.getMultiUnicode('director')
        g.getMultiUnicode('genres')

        try:
            movie.cast = [ unicode(p) + ' -- ' + unicode(p.currentRole) for p in movieImdb['cast'][:15] ]
        except KeyError:
            movie.cast = []

        return result


    @cachedmethod
    def getPoster(self, imdbID):
        """Return the low- and high-resolution posters (if available) of an imdb object."""
        imageDir = smewtUserDirectory('images')
        noposter = smewtDirectory('smewt', 'media', 'common', 'images', 'noposter.png')

        loresFilename, hiresFilename = None, None

        try:
            movieUrl = 'http://www.imdb.com/title/tt' + imdbID
            html = etree.HTML(curlget(movieUrl))
            poster = html.find(".//div[@class='photo']")
            loresURL = poster.find('.//img').get('src')
            loresFilename = os.path.join(imageDir, '%s_lores.jpg' % imdbID)
            open(loresFilename, 'wb').write(curlget(loresURL))
        except SmewtException:
            log.warning('Could not find poster for imdb ID %s' % imdbID)
            return (noposter, noposter)

        try:
            hiresLink = poster.find('.//a')
            if hiresLink.get('title') == 'Poster Not Submitted':
                raise SmewtException('Poster not available')
            hiresHtmlURL = 'http://www.imdb.com' + hiresLink.get('href')
            html = etree.HTML(curlget(hiresHtmlURL))
            hiresURL = html.find(".//div[@class='primary']").find('.//img').get('src')
            hiresFilename = os.path.join(imageDir, '%s_hires.jpg' % imdbID)
            open(hiresFilename, 'wb').write(curlget(hiresURL))
        except SmewtException:
            log.warning('Could not find hires poster for imdb ID %s' % imdbID)
            hiresFilename = noposter


        return (loresFilename, hiresFilename)


    def startEpisode(self, episode):
        if episode.get('series') is None:
            raise SmewtException("IMDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)

        name = episode.series.title
        try:
            series = self.getSeries(name)
            from smewt.base import cache
            #cache.save('/tmp/smewt.cache')
            eps = self.getEpisodes(series)
            #cache.save('/tmp/smewt.cache')

            lores, hires = self.getPoster(series.movieID)

            eps.find_one(Series).update({ 'loresImage': lores,
                                         'hiresImage': hires })

            return eps

        except Exception, e:
            log.warning(str(e) + ' -- ' + str(textutils.toUtf8(episode)))
            return MemoryObjectGraph()

    def startMovie(self, movieName):
        try:
            movieImdb = self.getMovie(movieName)
            result = self.getMovieData(movieImdb)

            movie = result.find_one('Movie')
            lores, hires = self.getPoster(movieImdb.movieID)
            movie.loresImage = lores
            movie.hiresImage = hires

            #result.displayGraph()
            return result

        except SmewtException, e:
            raise
            log.warning(str(e) + ' -- ' + textutils.toUtf8(movieName))
            return MemoryObjectGraph()
