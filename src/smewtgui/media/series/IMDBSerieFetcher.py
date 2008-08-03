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

from base import SmewtException
from urllib import urlopen
from smewt import utils
from media.series.serieobject import EpisodeObject
from smewt.webparser import WebParser
import re


class IMDBSerieFetcher(WebParser):
    def __init__(self):
        WebParser.__init__(self)

    def getSerieUrl(self, serieName):
        # FIXME: encode url correctly
        queryPage = 'http://www.imdb.com/find?s=all&q=%s&x=0&y=0' % serieName.replace(' ', '+') # use urlencode or sth?
        results = urlopen(queryPage).read()
        #results = open('/tmp/find.html').read()

        try:
            url = re.compile('<a href="([^"]*?)">&#34.*?TV series').findall(results)[0]
        except IndexError:
            raise SmewtException('Serie "%s" not found on IMDB...' % serieName)

        url = 'http://www.imdb.com' + url
        return url

    def getSeriePoster(self, serieName):
        serieUrl = self.getSerieUrl(serieName)
        html = urlopen(serieUrl).read()
        rexp = '<a name="poster" href="(?P<hiresUrl>[^"]*)".*?src="(?P<loresImg>[^"]*)"'
        poster = utils.matchRegexp(html, rexp)
        open('/tmp/lores.jpg', 'w').write(urlopen(poster['loresImg']).read())

        html = urlopen('http://www.imdb.com' + poster['hiresUrl']).read()
        rexp = '<table id="principal">.*?src="(?P<hiresImg>[^"]*)"'
        poster = utils.matchRegexp(html, rexp)
        open('/tmp/hires.jpg', 'w').write(urlopen(poster['hiresImg']).read())

    def getAllEpisodes(self, serieName):
        epsUrl = self.getSerieUrl(serieName) + 'episodes'
        epsHtml = urlopen(epsUrl).read()
        #epsHtml = open('/tmp/episodes.html').read()

        # get correct name for the serie
        serieName = utils.matchRegexp(epsHtml, '&#34;(?P<name>.*?)&#34;')['name']
        #print 'found serie name', serieName

        eps = []

        for line in epsHtml.split('\n'):
            #<a href="/title/tt0977178/">More with Less</a>
            if '<h4>Season ' in line and 'Episode ' in line:
                rexp = 'Season (?P<season>[0-9]+), Episode (?P<episodeNumber>[0-9]+)'
                rexp += '.*?<a href="(?P<imdbUrl>.*?)">(?P<title>.*?)</a>'
                md = utils.matchRegexp(line, rexp)
                md['serieName'] = serieName
                md['imdbUrl'] = 'http://www.imdb.com' + md['imdbUrl']
                md['synopsis'] = utils.matchRegexp(line, '<br>  (?P<synopsis>.*?)<br/>')['synopsis']

                try:
                    md['originalAirDate'] = utils.matchRegexp(line, 'Original Air Date: (?P<date>.*?)</b>')['date']
                except: pass

                md = self.cleanMetadata(md)

                eps.append(EpisodeObject.fromDict(md))

        return eps

    def cleanMetadata(self, md):
        for key, value in md.items():
            # convert to unicode
            # hardcoded for IMDB, but should be guessed from the html charset
            md[key] = value.decode('iso-8859-1')

            # convert html code chars to unicode
            md[key] = self.convertHtmlCodeChars(md[key])

        return md


if __name__ == '__main__':
    md = IMDBSerieFetcher()
    md.getSeriePoster('damages')
    #md.getSerieUrl('damages')
    eps = md.getAllEpisodes('damages')
    for ep in eps:
        print unicode(ep)
