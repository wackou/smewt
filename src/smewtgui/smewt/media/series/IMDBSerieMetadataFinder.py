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

from smewt import SmewtException, utils, cachedmethod
from smewt.media.series import Episode
from smewt.webparser import WebParser
from smewt.utils import matchRegexp
from urllib import urlopen
import re


class IMDBSerieMetadataFinder(WebParser):
    def __init__(self):
        WebParser.__init__(self)

    @cachedmethod
    def getSerieUrl(self, serieName):
        # FIXME: encode url correctly
        queryPage = 'http://www.imdb.com/find?s=all&q=%s&x=0&y=0' % serieName.replace(' ', '+') # use urlencode or sth?
        resultPage = urlopen(queryPage)

        # have we been sent directly to the corresponding page or are we still on the search page?
        try:
            url = matchRegexp(resultPage.geturl(), '(?P<url>http://www.imdb.com/title/tt[0-9]*/).*')['url']
            return url
        except SmewtException:
            pass

        results = resultPage.read()
        #results = open('/tmp/find.html').read()

        try:
            url = re.compile('<a href="([^"]*?)">&#34.*?TV series').findall(results)[0]
        except IndexError:
            raise SmewtException('Serie "%s" not found on IMDB...' % serieName)

        url = 'http://www.imdb.com' + url
        return url

    @cachedmethod
    def getSeriePoster(self, serieUrl):
        # FIXME: big hack!
        prefix = serieUrl.split('/')[-2]
        import os
        imageDir = os.getcwd()+'/smewt/media/series/images'
        os.system('mkdir -p "%s"' % imageDir)

        html = urlopen(serieUrl).read()
        rexp = '<a name="poster" href="(?P<hiresUrl>[^"]*)".*?src="(?P<loresImg>[^"]*)"'
        poster = utils.matchRegexp(html, rexp)
        loresFilename = imageDir + '/%s_lores.jpg' % prefix
        open(loresFilename, 'w').write(urlopen(poster['loresImg']).read())

        html = urlopen('http://www.imdb.com' + poster['hiresUrl']).read()
        rexp = '<table id="principal">.*?src="(?P<hiresImg>[^"]*)"'
        poster = utils.matchRegexp(html, rexp)
        hiresFilename = imageDir + '/%s_hires.jpg' % prefix
        open(hiresFilename, 'w').write(urlopen(poster['hiresImg']).read())

        return (loresFilename, hiresFilename)

    @cachedmethod
    def getAllEpisodes(self, serieName, serieUrl = None):
        if not serieUrl:
            serieUrl = self.getSerieUrl(serieName)
        epsUrl =  serieUrl + 'episodes'
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
                md['serie'] = serieName
                md['imdbUrl'] = 'http://www.imdb.com' + md['imdbUrl']
                md['synopsis'] = utils.matchRegexp(line, '<br>  (?P<synopsis>.*?)<br/>')['synopsis']

                try:
                    md['originalAirDate'] = utils.matchRegexp(line, 'Original Air Date: (?P<date>.*?)</b>')['date']
                except: pass

                md = self.cleanMetadata(md)

                eps.append(Episode.fromDict(md))

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
    md = IMDBSerieMetadataFinder()
    #md.getSerieUrl('damages')
    #md.getSeriePoster(md.getSerieUrl('damages'))
    eps = md.getAllEpisodes('black adder')
    for ep in eps:
        print unicode(ep)
