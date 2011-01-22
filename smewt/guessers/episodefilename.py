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
from smewt.base import Media, Metadata, SmewtException
from smewt.base.utils import tolist
from smewt.media import Episode, Series
import logging, re

log = logging.getLogger('smewt.guessers.episodefilename')


class EpisodeFilename(GraphAction):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(EpisodeFilename, self).__init__()

    def canHandle(self, query):
        if query.find_one(Media).type() not in [ 'video', 'subtitle' ]:
            raise SmewtException("%s: can only handle video or subtitle media objects" % self.__class__.__name__)

    def perform(self, query):
        self.checkValid(query)

        media = query.find_one(Media)

        log.debug('EpisodeFilename guesser working on file: %s' % media.filename)

        name = utils.splitPath(media.filename)
        filename = name[-1]

        # heuristic 1: try to guess the season & epnumber using S01E02 and 1x02 patterns
        sep = '[ \._-]'
        rexps = [ 'season (?P<season>[0-9]+)',
                  sep + '(?P<episodeNumber>[0-9]+)(?:v[23])?' + sep, # v2 or v3 for some mangas which have multiples rips
                  '(?P<season>[0-9]+)[x\.](?P<episodeNumber>[0-9]+)',
                  '[Ss](?P<season>[0-9]+) ?[Ee](?P<episodeNumber>[0-9]+)'
                  ]

        for n in name:
            for match in textutils.matchAllRegexp(n, rexps):
                log.debug('Found with confidence 1.0: %s' % match)
                ep = query.Episode(confidence = 1.0, allow_incomplete = True, **match)
                media.append('matches', ep)

        # cleanup a bit by removing unlikely eps numbers which are probably numbers in the title
        # or even dates in the filename, etc...
        niceGuess = None
        for md in tolist(media.get('matches')):
            if 'episodeNumber' in md and 'season' in md:
                niceGuess = md
            if 'episodeNumber' in md and 'season' not in md and md.episodeNumber > 1000:
                log.debug('Removing unlikely %s', str(md))
                query.delete_node(md.node)
        # if we have season+epnumber, remove single epnumber guesses
        if niceGuess:
            for md in query.find_all(node_type = Episode):
                if 'episodeNumber' in md and 'season' not in md:
                    log.debug('Removing %s because %s looks better' % (md, niceGuess))
                    query.delete_node(md.node)


        # heuristic 2: try to guess the serie title from the filename
        for rexp in rexps:
            result = re.compile(rexp, re.IGNORECASE).search(filename)
            if result:
                title = textutils.cleanString(filename[:result.span()[0]])
                log.debug('Found with confidence 0.6: series title = %s' % title)

                series = query.find_or_create(Series, title = title)
                media.append('matches', query.Episode(confidence = 0.6, allow_incomplete = True, series = series))


        # heuristic 3: try to guess the serie title from the parent directory!
        result = query.Episode(allow_incomplete = True)
        if textutils.matchAnyRegexp(name[-2], [ 'season (?P<season>[0-9]+)',
                                               # TODO: need to find a better way to have language packs for regexps
                                               'saison (?P<season>[0-9]+)' ]):
            log.debug('Found with confidence 0.8: series title = %s' % name[-3])
            s = query.find_or_create(Series, title = name[-3])
            result.series = s
            result.confidence = 0.8
            media.append('matches', result)

        else:
            log.debug('Found with confidence 0.4: series title = %s' % name[-2])
            s = query.find_or_create(Series, title = name[-2])
            result.series = s
            result.confidence = 0.4
            media.append('matches', result)

        # heuristic 4: add those anyway with very little probability, so that if don't find anything we can still use this
        media.append('matches', query.Episode(confidence = 0.1, series = query.Series(title = 'Unknown'), season = 1, episodeNumber = -1))

        # post-processing
        # we could already clean a bit the data here by solving it and comparing it to
        # each element we found, eg: remove all md which have an improbable episode number
        # such as 72 if some other valid episode number has been found, etc...

        # if the episode number is higher than 100, we assume it is season*100+epnumber
        for md in query.find_all(node_type = Episode, valid_node = lambda x: x.episodeNumber > 100):
            num = md.episodeNumber
            # it's the only guess we have, make it look like it's an episode
            # FIXME: maybe we should check if we already have an estimate for the season number?
            md.season = num // 100
            md.episodeNumber = num % 100


        return query
