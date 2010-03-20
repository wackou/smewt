#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from smewt.base import GraphAction, utils, textutils
from smewt.base import Media, Metadata
from smewt.base.utils import tolist
from smewt.media import Episode, Series
import logging

log = logging.getLogger('smewt.guessers.episodefilename')


class EpisodeFilename(GraphAction):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(EpisodeFilename, self).__init__()

    def canHandle(self, query):
        if query.findOne(Media).type() not in [ 'video', 'subtitle' ]:
            raise SmewtException("%s: can only handle video or subtitle media objects" % self.__class__.__name__)

    def perform(self, query):
        self.checkValid(query)

        media = query.findOne(Media)

        name = utils.splitFilename(media.filename)

        print '--',  name

        # heuristic 1: try to guess the season & epnumber using S01E02 and 1x02 patterns
        sep = '[ \._-]'
        rexps = [ 'season (?P<season>[0-9]+)',
                  sep + '(?P<episodeNumber>[0-9]+)(?:v[23])?' + sep, # v2 or v3 for some mangas which have multiples rips
                  '(?P<season>[0-9]+)[x\.](?P<episodeNumber>[0-9]+)',
                  'S(?P<season>[0-9]+)E(?P<episodeNumber>[0-9]+)'
                  ]

        for n in name:
            for match in textutils.matchAllRegexp(n, rexps):
                ep = query.Episode(confidence = 1.0, allowIncomplete = True, **match)
                media.append('matches', ep)

        # cleanup a bit by removing unlikely eps numbers which are probably numbers in the title
        # or even dates in the filename, etc...
        niceGuess = None
        for md in tolist(media.matches):
            if 'episodeNumber' in md and 'season' in md:
                niceGuess = md
            if 'episodeNumber' in md and 'season' not in md and md.episodeNumber > 1000:
                log.debug('Removing unlikely %s', str(md))
                query.deleteNode(md._node)
        # if we have season+epnumber, remove single epnumber guesses
        if niceGuess:
            for md in query.findAll(type = Episode):
                if 'episodeNumber' in md and 'season' not in md:
                    log.debug('Removing %s because %s looks better' % (md, niceGuess))
                    query.deleteNode(md._node)


        # heuristic 2: try to guess the serie title from the parent directory!
        result = query.Episode(allowIncomplete = True)
        if textutils.matchAnyRegexp(name[1], [ 'season (?P<season>[0-9]+)',
                                               # TODO: need to find a better way to have language packs for regexps
                                               'saison (?P<season>[0-9]+)' ]):
            s = query.findOrCreate(Series, title = name[2])
            result.series = s
            result.confidence = 0.8
        else:
            s = query.findOrCreate(Series, title = name[1])
            result.series = s
            result.confidence = 0.4

        media.append('matches', result)

        # post-processing
        # we could already clean a bit the data here by solving it and comparing it to
        # each element we found, eg: remove all md which have an improbable episode number
        # such as 72 if some other valid episode number has been found, etc...

        # if the episode number is higher than 100, we assume it is season*100+epnumber
        for md in query.findAll(type = Episode, validNode = lambda x: x.episodeNumber > 100):
            num = md.episodeNumber
            # it's the only guess we have, make it look like it's an episode
            # FIXME: maybe we should check if we already have an estimate for the season number?
            md.season = num // 100
            md.episodeNumber = num % 100


        return query
