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
from smewt.media import Movie

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb
from smewt.base import textutils

log = logging.getLogger('smewt.guessers.movieimdb')

class Getter:
    def __init__(self, md, d):
        self.md = md
        self.d = d

    def get(self, name, fromName = None):
        if not fromName:
            fromName = name
        try:
            self.md[name] = self.d[fromName]
        except:
            pass

class IMDBMetadataProvider(QObject):
    def __init__(self, movie):
        super(IMDBMetadataProvider, self).__init__()

        '''
        if not episode['series']:
            raise SmewtException("IMDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)
            '''

        self.movieName = movie
        self.imdb = imdb.IMDb()

    @cachedmethod
    def getMovie(self, name):
        log.debug('MovieIMDB: looking for movie %s', name)
        results = self.imdb.search_movie(name)
        for r in results:
            if r['kind'] == 'movie':
                return r
        raise SmewtException("EpisodeIMDB: Could not find movie '%s'" % name)

    def forwardData(self, d, dname, ep, epname):
        try:
            d[dname] = ep[epname]
        except: pass

    @cachedmethod
    def getMovieData(self, movieImdb):
        self.imdb.update(movieImdb)
        movie = Movie({ 'title': movieImdb['title'],
                        'year': movieImdb['year'],
                        'rating': movieImdb['rating'],
                        'director': [ unicode(p) for p in movieImdb['director'] ],
                        'writer': [ unicode(p) for p in movieImdb['writer'] ],
                        'genres': [ unicode(p) for p in movieImdb['genres'] ],
                        #'plot': movieImdb['plot'],
                        #'plotOutline': movieImdb['plot outline'],
                        })
        g = Getter(movie, movieImdb)
        g.get('plot')
        g.get('plotOutline', 'plot outline')

        try:
            movie['cast'] = [ (unicode(p), unicode(p.currentRole)) for p in movieImdb['cast'][:15] ]
        except:
            movie['cast'] = []

        return movie

    @cachedmethod
    def getMoviePoster(self, movieID):
        # FIXME: big hack!
        import os
        imageDir = os.getcwd()+'/smewt/media/movie/images'
        os.system('mkdir -p "%s"' % imageDir)

        loresFilename, hiresFilename = None, None

        try:
            movieUrl = 'http://www.imdb.com/title/tt' + movieID
            html = urlopen(movieUrl).read()
            rexp = '<a name="poster" href="(?P<hiresUrl>[^"]*)".*?src="(?P<loresImg>[^"]*)"'
            poster = textutils.matchRegexp(html, rexp)
            loresFilename = imageDir + '/%s_lores.jpg' % movieID
            open(loresFilename, 'w').write(urlopen(poster['loresImg']).read())
        except Exception, e:
            log.warning('Could not find lores poster for imdb ID %s because: %s' % (movieID, str(e)))

        try:
            html = urlopen('http://www.imdb.com' + poster['hiresUrl']).read()
            rexp = '<table id="principal">.*?src="(?P<hiresImg>[^"]*)"'
            poster = textutils.matchRegexp(html, rexp)
            hiresFilename = imageDir + '/%s_hires.jpg' % movieID
            open(hiresFilename, 'w').write(urlopen(poster['hiresImg']).read())
        except Exception, e:
            log.warning('Could not find hires poster for imdb ID %s because: %s' % (movieID, str(e)))

        return (loresFilename, hiresFilename)


    def start(self):
        try:
            movieImdb = self.getMovie(self.movieName)
            movie = self.getMovieData(movieImdb)
            lores, hires = self.getMoviePoster(movieImdb.movieID)
            movie['loresImage'] = lores
            movie['hiresImage'] = hires

            self.emit(SIGNAL('finished'), movie)

        except Exception, e:
            log.warning(str(e) + ' -- ' + str(self.movieName))
            self.emit(SIGNAL('finished'), self.movieName, [])



class MovieIMDB(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def start(self, query):
        self.checkValid(query)
        self.query = query

        log.debug('MovieImdb: finding more info on %s' % query.findAll(Media))
        movie = query.findOne(Movie)
        # if valid movie

        self.mdprovider = IMDBMetadataProvider(movie['title'])
        self.connect(self.mdprovider, SIGNAL('finished'),
                     self.queryFinished)
        self.mdprovider.start()

    def queryFinished(self, guess):
        del self.mdprovider # why is that useful again?

        media = self.query.findOne(Media)
        media.metadata = guess
        result = Graph()
        result += media

        self.emit(SIGNAL('finished'), result)
