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
from smewt.datamodel import MemoryObjectGraph

from PyQt4.QtCore import SIGNAL, QObject, QUrl

import os, sys, re, logging
from urllib import urlopen,  urlencode
from smewt.base.utils import curlget
import thetvdbapi

log = logging.getLogger('smewt.guessers.tvdbmetadataprovider')

class TVDBMetadataProvider(object):
    def __init__(self):
        super(TVDBMetadataProvider, self).__init__()

        self.tvdb = thetvdbapi.TheTVDB("65D91F0290476F3E")

    @cachedmethod
    def getSeries(self, name):
        """Get the TVDBPy series object given its name."""
        results = self.tvdb.get_matching_shows(name)
        for id, name in results:
            return id
        raise SmewtException("EpisodeTVDB: Could not find series '%s'" % name)


    @cachedmethod
    def getEpisodes(self, series):
        """From a given TVDBPy series object, return a graph containing its information
        as well as its episodes nodes."""
        show, episodes = self.tvdb.get_show_and_episodes(series)

        # TODO: debug to see if this is the correct way to access the series' title
        result = MemoryObjectGraph()
        smewtSeries = result.Series(title = show.name)

        # FIXME: find a better way to know whether there are episodes or not
        if len(episodes)==0:
          return result

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
        raise SmewtException("MovieTVDB: Could not find movie '%s'" % name)

    @cachedmethod
    def getMovieData(self, movieTvdb):
        """From a given TVDBPy movie object, return a graph containing its information."""
        result = MemoryObjectGraph()
        return result


    @cachedmethod
    def getPoster(self, tvdbID):
        """Return the low- and high-resolution posters (if available) of an tvdb object."""
        imageDir = smewtUserDirectory('images')
        noposter = smewtDirectory('smewt', 'media', 'common', 'images', 'noposter.png')

        loresFilename, hiresFilename = None, None
        
        urls = self.tvdb.get_show_image_choices(tvdbID)
        posters = [url for url in urls if url[1]=='poster']
        if len(posters)>0:
            loresURL = posters[0][0]
            loresFilename = os.path.join(imageDir, '%s_lores.jpg' % tvdbID)
            open(loresFilename, 'wb').write(curlget(loresURL))
            
            if len(posters)>1:
              hiresURL = posters[1][0]
              hiresFilename = os.path.join(imageDir, '%s_hires.jpg' % tvdbID)
              open(hiresFilename, 'wb').write(curlget(hiresURL))        
        else:
            log.warning('Could not find poster for tvdb ID %s' % tvdbID)
            return (noposter, noposter)

        return (loresFilename, hiresFilename)


    def startEpisode(self, episode):
        if episode.get('series') is None:
            raise SmewtException("TVDBMetadataProvider: Episode doesn't contain 'series' field: %s", md)

        name = episode.series.title
        try:
            series = self.getSeries(name)
            from smewt.base import cache
            #cache.save('/tmp/smewt.cache')
            eps = self.getEpisodes(series)
            #cache.save('/tmp/smewt.cache')
            lores, hires = self.getPoster(series)
            eps.findOne(Series).update({ 'loresImage': lores,
                                         'hiresImage': hires })
            return eps

        except Exception, e:
            log.warning(str(e) + ' -- ' + str(textutils.toUtf8(episode)))
            return MemoryObjectGraph()

    def startMovie(self, movieName):
        try:
            movieTvdb = self.getMovie(movieName)
            result = self.getMovieData(movieTvdb)

            movie = result.findOne('Movie')
            lores, hires = self.getPoster(movieTvdb)
            movie.loresImage = lores
            movie.hiresImage = hires

            #result.displayGraph()
            return result

        except SmewtException, e:
            raise
            log.warning(str(e) + ' -- ' + textutils.toUtf8(movieName))
            return MemoryObjectGraph()

