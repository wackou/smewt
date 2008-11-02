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

import re
from urllib import urlopen, urlencode
from smewt import utils, SmewtException

def simpleMatch(string, regexp):
    return re.compile(regexp).search(string).groups()[0]

def between(string, left, right):
    return string.split(left)[1].split(right)[0]

class TVSubtitlesProvider:

    baseUrl = 'http://www.tvsubtitles.net'

    def getLikelySeriesUrl(self, name):
        data = urlencode({ 'q': name })
        searchHtml = urlopen(self.baseUrl + '/search.php', data).read()
        resultsHtml = between(searchHtml, 'Search results', '<div id="right">')
        rexp = '<a href="(?P<url>.*?)">(?P<title>.*?)</a>'
        matches = utils.multipleMatchRegexp(resultsHtml, rexp)

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

    def getSeriesID(self, name):
        # TODO: get most likely one if more than one found
        url = self.getLikelySeriesUrl(name)[0]['url']
        return simpleMatch(url, 'tvshow-(.*?).html')

    def getEpisodeID(self, series, season, number):
        seriesID = self.getSeriesID(series)
        seasonHtml = urlopen(self.baseUrl + '/tvshow-%s-%d.html' % (seriesID, season)).read()
        try:
            episodeRowHtml = between(seasonHtml, '%dx%02d' % (season, number), '</tr>')
        except IndexError:
            raise SmewtException("Season %d Episode %d unavailable for series '%s'" % (season, number, series))
        return simpleMatch(episodeRowHtml, 'episode-(.*?).html')

    def parseSubtitleInfo(self, string):
        result = {}
        result['id'] = simpleMatch(string, 'subtitle-(.*?).html')
        result['code'] = simpleMatch(string, 'flags/(.*?).gif')
        result['title'] = simpleMatch(string, 'hspace=4>(.*?)</h5>')
        return result

    def getAvailableSubtitlesID(self, series, season, number):
        episodeID = self.getEpisodeID(series, season, number)
        episodeHtml = urlopen(self.baseUrl + '/episode-%s.html' % episodeID).read()
        subtitlesHtml = between(episodeHtml, 'Subtitles for this episode:', '<br clear=all>')

        result = [ self.parseSubtitleInfo(s['sub'])
                   for s in utils.multipleMatchRegexp(subtitlesHtml, '(?P<sub><a href=.*?</a>)') ]

        return result



if __name__ == '__main__':
    series, season, episode, language = 'heroes', 3, 5, 'fr'

    tvsub = TVSubtitlesProvider()
    subs = tvsub.getAvailableSubtitlesID(series, season, episode)

    for sub in subs:
        if sub['code'] == language:
            tmpfile = '/tmp/sub.zip'

            # urllib is not able to correctly follow the URL with spaces in it, use urllib2
            import urllib2
            f = open(tmpfile, 'wb')
            f.write(urllib2.urlopen('http://www.tvsubtitles.net/download-%s.html' % sub['id']).read())
            f.close()

            import zipfile
            zf = zipfile.ZipFile(tmpfile)
            filename = zf.infolist()[0].filename
            subtext = zf.read(filename)
            subf = open('/tmp/' + filename, 'w')
            subf.write(subtext)
            unicodeSub = subtext.decode('iso-8859-1')

            import locale
            print 'Found subtitle:', filename
            print
            print unicodeSub.encode(locale.getdefaultlocale()[1])
