#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
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

from smewt.base import cachedmethod, SmewtException
from smewt.media import Series
from smewt.base import textutils
from smewt.base.utils import tolist, smewtDirectory, smewtUserDirectory
from pygoo import MemoryObjectGraph
import guessit
from PyQt4.QtCore import Qt, QSettings
from PyQt4.QtGui import QImage
import os
from urllib2 import urlopen
import thetvdbapi
import tmdb
import datetime
import logging

log = logging.getLogger(__name__)

def guiLanguage():
    language = str(QSettings().value('gui/language', 'en').toString())
    return guessit.Language(language)


class TVDBMetadataProvider(object):
    def __init__(self):
        super(TVDBMetadataProvider, self).__init__()

        self.tvdb = thetvdbapi.TheTVDB("65D91F0290476F3E")
        self.tmdb = tmdb.MovieDb()

    @cachedmethod
    def getSeries(self, name):
        """Get the TVDBPy series object given its name."""
        results = self.tvdb.get_matching_shows(name)
        '''
        for id, name, lang in results:
            # FIXME: that doesn't look correct: either yield or no for
            return id
        raise SmewtException("EpisodeTVDB: Could not find series '%s'" % name)
        '''
        if len(results)==0:
          raise SmewtException("EpisodeTVDB: Could not find series '%s'" % name)

        return results

    @cachedmethod
    def getEpisodes(self, series, language):
        """From a given TVDBPy series object, return a graph containing its information
        as well as its episodes nodes."""
        show, episodes = self.tvdb.get_show_and_episodes(series, language=language)

        # TODO: debug to see if this is the correct way to access the series' title
        result = MemoryObjectGraph()
        smewtSeries = result.Series(title = show.name)

        for episode in episodes:
            ep = result.Episode(series = smewtSeries,
                                season = episode.season_number,
                                episodeNumber = episode.episode_number)
            ep.set('title', episode.name)
            ep.set('synopsis', episode.overview)
            ep.set('originalAirDate', str(episode.first_aired))

        return result

    @cachedmethod
    def getMovie(self, name):
        """Get the IMDBPy movie object given its name."""
        if not name:
            raise SmewtException('You need to specify at least a probable name for the movie...')
        log.debug('MovieTMDB: looking for movie %s', name)
        results = self.tmdb.search(name)
        for r in results:
          return r['id']

        raise SmewtException("MovieTMDB: Could not find movie '%s'" % name)

    @cachedmethod
    def getMovieData(self, movieId):
        """From a given TVDBPy movie object, return a graph containing its information."""
        m = self.tmdb.getMovieInfo(movieId)

        result = MemoryObjectGraph()
        movie = result.Movie(title = unicode(m['name']))
        movie.original_title = m['original_name']

        if m.get('released'):
            movie.set('year', datetime.datetime.strptime(m['released'], '%Y-%m-%d').year)

        movie.set('director', [unicode(d['name']) for d in m['cast'].get('director', [])])
        movie.set('writer', [unicode(d['name']) for d in m['cast'].get('author', [{'name': ''}])])
        movie.set('genres', [unicode(g) for g in m['categories'].get('genre', {}).keys()])
        movie.set('rating', m['rating'])
        movie.set('plot', [unicode(m['overview'])])

        try:
            movie.cast = [ unicode(actor['name']) + ' -- ' + unicode(actor['character']) for actor in m['cast']['actor'][:15] ]
        except KeyError:
            movie.cast = []


        return result

    def savePoster(self, posterUrl, localId):
        imageDir = smewtUserDirectory('images')

        hiresFilename = os.path.join(imageDir, '%s_hires.jpg' % localId)
        open(hiresFilename, 'wb').write(urlopen(posterUrl).read())

        # lores = 80px high
        loresFilename = os.path.join(imageDir, '%s_lores.jpg' % localId)
        image = QImage()
        image.load(hiresFilename)
        image.scaledToHeight(80, Qt.SmoothTransformation).save(loresFilename)

        return '/user/images/%s_lores.jpg' % localId, '/user/images/%s_hires.jpg' % localId

    @cachedmethod
    def getSeriesPoster(self, tvdbID):
        """Return the low- and high-resolution posters of a tvdb object."""
        noposter = '/static/images/noposter.png'

        urls = self.tvdb.get_show_image_choices(tvdbID)
        posters = [url for url in urls if url[1] == 'poster']
        if posters:
            return self.savePoster(posters[0][0], 'series_%s' % tvdbID)

        else:
            log.warning('Could not find poster for tvdb ID %s' % tvdbID)
            return (noposter, noposter)


    @cachedmethod
    def getMoviePoster(self, movieId):
        """Return the low- and high-resolution posters (if available) of an tvdb object."""
        noposter = smewtDirectory('smewt', 'media', 'common', 'images', 'noposter.png')

        m = self.tmdb.getMovieInfo(movieId)

        posters = []
        for poster in m['images'].posters:
            for key, value in poster.items():
                if key not in ['id', 'type']:
                    if value.startswith("http://"):
                      posters.append(value)


        if posters:
            return self.savePoster(posters[0], 'movie_%s' % movieId)

        else:
            log.warning('Could not find poster for tmdb ID %s' % movieId)
            return (noposter, noposter)



    def startEpisode(self, episode):
        tmdb.config['lang'] = guiLanguage().alpha2
        tmdb.update_config()

        if episode.get('series') is None:
            raise SmewtException("TVDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)

        name = episode.series.title
        name = name.replace(',', ' ')

        matching_series = self.getSeries(name)

        # Try first with the languages from guessit, and then with english
        languages = tolist(episode.get('language', [])) + ['en']

        # Sort the series by id (stupid heuristic about most popular series
        #                        might have been added sooner to the db and the db id
        #                        follows the insertion order)
        # TODO: we should do something smarter like comparing series name distance,
        #       episodes count and/or episodes names
        #print '\n'.join(['%s %s --> %f [%s] %s' % (x[1], name, textutils.levenshtein(x[1], name), x[2], x[0]) for x in matching_series])
        matching_series.sort(key=lambda x: (textutils.levenshtein(x[1], name), int(x[0])))

        series = None
        language = 'en'
        for lang in languages:
            try:
                language = lang
                ind = zip(*matching_series)[2].index(lang)
                series = matching_series[ind][0]
                break
            except ValueError, e:
                language = matching_series[0][2]
                series = matching_series[0][0]

        # TODO: at the moment, overwrite the detected language with the one
        #       from the settings. It would be better to use the detected
        #       language if it was more reliable (see previous TODO)...
        language = guiLanguage().alpha2

        eps = self.getEpisodes(series, language)

        try:
            lores, hires = self.getSeriesPoster(series)
            eps.find_one(Series).update({ 'loresImage': lores,
                                          'hiresImage': hires })
            return eps

        except Exception, e:
            log.warning(str(e) + ' -- ' + str(textutils.toUtf8(episode)))
            return MemoryObjectGraph()

    def startMovie(self, movieName):
        tmdb.config['lang'] = guiLanguage().alpha2
        tmdb.update_config()

        try:
            movieTvdb = self.getMovie(movieName)
            result = self.getMovieData(movieTvdb)

            movie = result.find_one('Movie')
            lores, hires = self.getMoviePoster(movieTvdb)
            movie.loresImage = lores
            movie.hiresImage = hires

            #result.display_graph()
            return result

        except SmewtException, e:
            raise
