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

from smewt.base import GraphAction, cachedmethod, utils, SmewtException, Media
from smewt.base.utils import smewtDirectory
from smewt.guessers.guesser import Guesser
from smewt.media.series import Episode, Series
from smewt.base.mediaobject import foundMetadata
from pygoo import MemoryObjectGraph, Equal
from urllib import urlopen,  urlencode
from tvdbmetadataprovider import TVDBMetadataProvider
import logging

log = logging.getLogger('smewt.guessers.episodeimdb')


class EpisodeTVDB(GraphAction):

    def canHandle(self, query):
        if query.find_one(Media).type() not in [ 'video', 'subtitle' ]:
            raise SmewtException("%s: can only handle video or subtitle media objects" % self.__class__.__name__)

    def perform(self, query):
        self.checkValid(query)
        self.query = query

        ep = query.find_one(Episode)

        log.debug('EpisodeTvdb: finding more info on %s' % ep)
        if ep.get('series') is None:
            raise SmewtException("EpisodeTVDB: Episode doesn't contain 'series' field: %s" % ep)

        # little hack: if we have no season number, add 1 as default season number
        # (helps for series which have only 1 season)
        if ep.get('season') is None:
            ep.season = 1

        try:
            mdprovider = TVDBMetadataProvider()
            result = mdprovider.startEpisode(ep)

        except SmewtException, e:
            # series could not be found, return a dummy Unknown series instead so we can group them somewhere
            log.warning('Could not find series for file: %s' % query.find_one(Media).filename)
            noposter = smewtDirectory('smewt', 'media', 'common', 'images', 'noposter.png')
            result = MemoryObjectGraph()
            result.Series(title = 'Unknown', loresImage = noposter, hiresImage = noposter)

        # update the series
        query.delete_node(ep.series.node)
        ep.series = query.add_object(result.find_one(Series)) # this add_object should be unnecessary

        # and add all the potential episodes
        for ep in result.find_all(Episode):
            query.add_object(ep, recurse = Equal.OnLiterals)


        return query
