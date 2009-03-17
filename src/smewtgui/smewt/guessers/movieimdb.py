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
from smewt.media.movie import Movie

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys, re, logging
from urllib import urlopen,  urlencode
import imdb
from smewt.base.textutils import stripBrackets

class IMDBMetadataProvider(QObject):
    def __init__(self, movie, metadata):
        super(IMDBMetadataProvider, self).__init__()

        '''
        if not episode['series']:
            raise SmewtException("IMDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)
            '''

        self.movieName = movie
        self.metadata = metadata
        self.imdb = imdb.IMDb()

    @cachedmethod
    def getMovie(self, name):
        logging.debug('MovieIMDB: looking for movie %s', name)
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
                        'year': movieImdb['year']
                        })
        return movie

    @cachedmethod
    def getMoviePoster(self, seriesID):
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
        try:
            movieImdb = self.getMovie(self.movieName)
            movie = self.getMovieData(movieImdb)
            lores, hires = self.getMoviePoster(movieImdb.movieID)
            movie['loresImage'] = lores
            movie['hiresImage'] = hires

            self.emit(SIGNAL('finished'), self.movieName, movie)

        except Exception, e:
            logging.warning(str(e) + ' -- ' + str(self.movieName))
            self.emit(SIGNAL('finished'), self.movieName, [])


def cleanMovieFilename(filename):
    import os.path
    filename = os.path.basename(filename)

    seps = [ ' ', '-', '.', '_' ]
    for sep in seps:
        filename = filename.replace(sep, ' ')

    name = filename.split(' ')

    properties = { 'format': [ 'DVDRip', 'HDDVD', 'BDRip', 'R5' ],
                   'container': [ 'avi', 'mkv', 'ogv', 'wmv', 'mp4', 'mov' ],
                   'screenSize': [ '720p' ],
                   'videoCodec': [ 'XviD', 'DivX', 'x264' ],
                   'audioCodec': [ 'AC3', 'DTS', 'AAC' ],
                   'language': [ 'english', 'eng',
                                 'spanish', 'esp',
                                 'vo', 'vf'
                                 ],
                   'releaseGroup': [ 'ESiR', 'WAF', 'SEPTiC', '[XCT]', 'iNT', 'PUKKA', 'CHD' ],
                   'other': [ '5ch', 'PROPER', 'REPACK',
                              'ws', # widescreen
                              ],
                   }

    # ensure they're all lowercase
    for prop, value in properties.items():
        properties[prop] = [ s.lower() for s in value ]

    md = {}

    # get specific properties
    for prop, value in properties.items():
        for part in list(name):
            if part.lower() in value:
                md[prop] = part
                name.remove(part)

    # get year
    def validYear(year):
        try:
            return int(year) > 1920 and int(year) < 2015
        except ValueError:
            return False


    for part in list(name):
        year = stripBrackets(part)
        if validYear(year):
            md['year'] = int(year)
            name.remove(part)

    # remove ripper name
    for by, who in zip(name[:-1], name[1:]):
        if by.lower() == 'by':
            name.remove(by)
            name.remove(who)
            md['ripper'] = who

    # subtitles
    for sub, lang in zip(name[:-1], name[1:]):
        if sub.lower() == 'sub':
            name.remove(sub)
            name.remove(lang)
            md['subtitleLanguage'] = lang

    # get CD number (if any)
    cdrexp = re.compile('[Cc][Dd]([0-9]+)')
    for part in list(name):
        try:
            md['cdNumber'] = int(cdrexp.search(part).groups()[0])
            name.remove(part)
        except AttributeError:
            pass

    name = ' '.join(name)

    # last chance on the full name: try some popular regexps
    rexps = [ '(?P<dircut>director\'s cut)' ]
    matched = utils.matchAllRegexp(name, rexps)
    for match in matched:
        for key, value in match.items():
            name = name.replace(value, '')

    # remove leftover tokens
    name = name.replace('()', '')
    name = name.replace('[]', '')


    return (name, md)




class MovieIMDB(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def start(self, query):
        self.checkValid(query)
        self.query = query

        logging.debug('MovieImdb: finding more info on %s' % query.findAll(Media))
        movie = query.findOne(Media)
        # if valid movie

        name, md = cleanMovieFilename(movie.filename)

        self.mdprovider = IMDBMetadataProvider(name, md)
        self.connect(self.mdprovider, SIGNAL('finished'),
                     self.queryFinished)
        self.mdprovider.start()

    def queryFinished(self, name, guess):
        del self.mdprovider # why is that useful again?

        # TODO: should we set self.query = guesses here?
        self.query.findOne(Media).metadata = guess
        self.query += guess

        self.emit(SIGNAL('finished'), self.query)
