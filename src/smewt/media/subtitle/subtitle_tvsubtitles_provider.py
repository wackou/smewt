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
from urllib import urlopen, urlencode
from smewt.base import textutils, utils, SmewtException, cachedmethod
from smewt.media import Episode, Series
from subtitleobject import Subtitle

def simpleMatch(string, regexp):
    return re.compile(regexp).search(string).groups()[0]

def between(string, left, right):
    return string.split(left)[1].split(right)[0]

class TVSubtitlesProvider:

    baseUrl = 'http://www.tvsubtitles.net'

    @cachedmethod
    def getLikelySeriesUrl(self, name):
        data = urlencode({ 'q': name })
        searchHtml = urlopen(self.baseUrl + '/search.php', data).read()
        resultsHtml = between(searchHtml, 'Search results', '<div id="right">')
        rexp = '<a href="(?P<url>.*?)">(?P<title>.*?)</a>'
        matches = textutils.multipleMatchRegexp(resultsHtml, rexp)

        # add baseUrl and remove year information
        for match in matches:
            try:
                idx = match['title'].find('(') - 1
                match['title'] = match['title'][:idx]
            except: pass
            match['url'] = self.baseUrl + match['url']

        if not matches:
            raise SmewtException("Couldn't find any matching series for '%s'" % name)

        return matches

    @cachedmethod
    def getSeriesID(self, name):
        # get most likely one if more than one found
        # FIXME: this hides another potential bug which is that tvsubtitles returns a lot of
        # false positives that it doesn't return when using from a "normal" webbrowser...
        urls = [ (textutils.levenshtein(s['title'], name), s) for s in self.getLikelySeriesUrl(name) ]
        url = sorted(urls)[0][1]['url']
        return simpleMatch(url, 'tvshow-(.*?).html')

    @cachedmethod
    def getEpisodeID(self, series, season, number):
        seriesID = self.getSeriesID(series)
        seasonHtml = urlopen(self.baseUrl + '/tvshow-%s-%d.html' % (seriesID, season)).read()
        try:
            episodeRowHtml = between(seasonHtml, '%dx%02d' % (season, number), '</tr>')
        except IndexError:
            raise SmewtException("Season %d Episode %d unavailable for series '%s'" % (season, number, series))
        return simpleMatch(episodeRowHtml, 'episode-(.*?).html')

    def parseSubtitleInfo(self, string):
        result = Subtitle()
        result['tvsubid'] = simpleMatch(string, 'subtitle-(.*?).html')
        result['language'] = simpleMatch(string, 'flags/(.*?).gif')
        result['title'] = simpleMatch(string, 'hspace=4>(.*?)</h5>')
        return result

    @cachedmethod
    def getAvailableSubtitlesID(self, series, season, number):
        episodeID = self.getEpisodeID(series, season, number)
        episodeHtml = urlopen(self.baseUrl + '/episode-%s.html' % episodeID).read()
        subtitlesHtml = between(episodeHtml, 'Subtitles for this episode', 'Back to')

        result = [ self.parseSubtitleInfo(s['sub'])
                   for s in textutils.multipleMatchRegexp(subtitlesHtml, '(?P<sub><a href=.*?</a>)') ]

        return result

    def downloadSubtitle(self, basename, series, season, episode, language, videoFilename = None):
        """videoFilename is just used a hint when we find multiple subtitles"""
        import cStringIO, zipfile, os.path
        subs = [ sub for sub in self.getAvailableSubtitlesID(series, season, episode) if sub['language'] == language ]

        if not subs:
            return

        sub = subs[0]
        if len(subs) > 1:
            logging.warning('More than 1 possible subtitle found: %s', str(subs))
            if videoFilename:
                dists = [ (textutils.levenshtein(videoFilename, sub['title']), sub) for sub in subs ]
                sub = sorted(dists)[0][1]
            logging.warning('Choosing %s' % sub)

        cd = utils.CurlDownloader()
        # first get this page to get session cookies...
        cd.get(self.baseUrl + '/subtitle-%s.html' % sub['id'])
        # ...then grab the sub file
        cd.get(self.baseUrl + '/download-%s.html' % sub['id'])

        zf = zipfile.ZipFile(cStringIO.StringIO(cd.contents))
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

    def titleFilter(self, title):
        return lambda x: x['series'] == Series({ 'title': title })

    def getAvailableSubtitles(self, metadata):
        try:
            if not metadata['season']:
                raise SmewtException('\'season\' attribute not in object')
            if not metadata['episodeNumber']:
                raise SmewtException('\'episodeNumber\' attribute not in object')
        except SmewtException, e:
            log.warning('TVSubtitlesProvider: %s' % str(e))
            return []

        return self.getAvailableSubtitlesID(metadata['series']['title'],
                                            metadata['season'],
                                            metadata['episodeNumber'])


    def getSubtitle(self, subtitle):
        '''This method should return the contents of the given subtitle as a string.
        The Subtitle object should be picked among the ones returned by the getAvailableSubtitles
        method.

        If the subtitle could not be found, a SubtitleNotFoundError exception should be raised.'''
        import cStringIO, zipfile, os.path

        cd = utils.CurlDownloader()
        # first get this page to get session cookies...
        cd.get(self.baseUrl + '/subtitle-%s.html' % subtitle['tvsubid'])
        # ...then grab the sub file
        cd.get(self.baseUrl + '/download-%s.html' % subtitle['tvsubid'])

        zf = zipfile.ZipFile(cStringIO.StringIO(cd.contents))
        filename = zf.infolist()[0].filename
        #extension = os.path.splitext(filename)[1]
        subtext = zf.read(filename)

        return subtext
