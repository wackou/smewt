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

import re, logging
from urllib import urlencode
from urllib2 import urlopen
from smewt.base import utils, SmewtException, cachedmethod
from pygoo import ontology, MemoryObjectGraph
from smewt.base.textutils import simpleMatch, between, levenshtein
from subtitleobject import Subtitle
from lxml import etree
ontology.import_classes([ 'Movie', 'Series', 'Episode' ])

log = logging.getLogger('TVSubtitlesProvider')


class TVSubtitlesProvider:

    baseUrl = 'http://www.tvsubtitles.net'

    @cachedmethod
    def getLikelySeriesUrl(self, name):
        data = urlencode({ 'q': name })
        html = etree.HTML(urlopen(self.baseUrl + '/search.php', data).read())
        matches = [ s.find('a') for s in html.findall(".//div[@style='']") ]

        # add baseUrl and remove year information
        result = []
        for match in matches:
            seriesID = int(match.get('href').split('-')[1].split('.')[0]) # remove potential season number
            seriesUrl = self.baseUrl + '/tvshow-%d.html' % seriesID
            title = match.text
            try:
                idx = title.find('(') - 1
                title = title[:idx]
            except: pass

            result.append({ 'title': title, 'url': seriesUrl })

        if not matches:
            raise SmewtException("Couldn't find any matching series for '%s'" % name)

        return result

    @cachedmethod
    def getSeriesID(self, name):
        # get most likely one if more than one found
        # FIXME: this hides another potential bug which is that tvsubtitles returns a lot of
        # false positives that it doesn't return when using from a "normal" webbrowser...
        urls = [ (levenshtein(s['title'], name), s) for s in self.getLikelySeriesUrl(name) ]
        url = sorted(urls)[0][1]['url']
        return int(simpleMatch(url, 'tvshow-(.*?).html'))

    @cachedmethod
    def getEpisodeID(self, series, season, number):
        seriesID = self.getSeriesID(series)
        seasonHtml = urlopen(self.baseUrl + '/tvshow-%d-%d.html' % (seriesID, season)).read()
        try:
            episodeRowHtml = between(seasonHtml, '%dx%02d' % (season, number), '</tr>')
        except IndexError:
            raise SmewtException("Season %d Episode %d unavailable for series '%s'" % (season, number, series))
        return int(simpleMatch(episodeRowHtml, 'episode-(.*?).html'))

    #@cachedmethod
    # cachedmethod doesn't work because of weakrefs in the graph...
    def getAvailableSubtitlesID(self, episode):
        log.debug('Getting subtitles id for %s %dx%2d' % (episode.series.title, episode.season, episode.episodeNumber))
        episodeID = self.getEpisodeID(episode.series.title, episode.season, episode.episodeNumber)
        episodeURL = self.baseUrl + '/episode-%d.html' % episodeID
        episodeHtml = urlopen(episodeURL).read()
        subtitlesHtml = between(episodeHtml, 'Subtitles for this episode', 'Back to')

        result = MemoryObjectGraph()
        ep = result.Episode(episode)

        episodeHtml = between(episodeHtml, '<b>Subtitles for this episode:</b>', '<br clear=all>')
        ehtml = etree.HTML(episodeHtml)

        for slink, sub in zip(ehtml.findall('.//a'),
                              ehtml.findall(".//div[@class='subtitlen']")):
            result.Subtitle(metadata = ep,
                            language = simpleMatch(sub.find('.//img').get('src'), 'flags/(.*?).gif'),
                            tvsubid = int(between(slink.get('href'), '-', '.')),
                            title = (sub.find('.//h5').find('img').tail or '').strip(),
                            source = (sub.find(".//p[@title='rip']").find('img').tail or '').strip(),
                            release = (sub.find(".//p[@title='release']").find('img').tail or '').strip())

        return result


    def downloadSubtitle(self, basename, series, season, episode, language, videoFilename = None):
        """videoFilename is just used a hint when we find multiple subtitles"""
        import cStringIO, zipfile, os.path
        subs = [ sub for sub in self.getAvailableSubtitlesID(series, season, episode) if sub['language'] == language ]

        if not subs:
            return

        sub = subs[0]
        if len(subs) > 1:
            log.warning('More than 1 possible subtitle found: %s', str(subs))
            if videoFilename:
                dists = [ (levenshtein(videoFilename, sub['title']), sub) for sub in subs ]
                sub = sorted(dists)[0][1]
            log.warning('Choosing %s' % sub)

        zippedSub = urlopen(self.baseUrl + '/download-%s.html' % sub['id']).read()

        zf = zipfile.ZipFile(cStringIO.StringIO(zippedSub))
        filename = zf.infolist()[0].filename
        extension = os.path.splitext(filename)[1]
        subtext = zf.read(filename)
        resultFilename = basename + extension
        subf = open(resultFilename, 'w')
        subf.write(subtext)
        subf.close()
        return resultFilename

    # everything down from here is the implementation of the SubtitleProvider interface
    def canHandle(self, metadata):
        return isinstance(metadata, Episode)

    #def titleFilter(self, title):
    #    return lambda x: x.series.title == title

    def getAvailableSubtitles(self, metadata):
        try:
            if metadata.get('season') is None:
                raise SmewtException("'season' attribute not in object")
            if metadata.get('episodeNumber') is None:
                raise SmewtException("'episodeNumber' attribute not in object")
        except SmewtException, e:
            log.warning('TVSubtitlesProvider: %s' % str(e))
            return []

        return self.getAvailableSubtitlesID(metadata)


    def getSubtitle(self, subtitle):
        '''This method should return the contents of the given subtitle as a string.
        The Subtitle object should be picked among the ones returned by the getAvailableSubtitles
        method.

        If the subtitle could not be found, a SubtitleNotFoundError exception should be raised.'''
        import cStringIO, zipfile, os.path

        zippedSub = urlopen(self.baseUrl + '/download-%d.html' % subtitle.tvsubid).read()

        zf = zipfile.ZipFile(cStringIO.StringIO(zippedSub))
        filename = zf.infolist()[0].filename
        #extension = os.path.splitext(filename)[1]
        subtext = zf.read(filename)

        return subtext
