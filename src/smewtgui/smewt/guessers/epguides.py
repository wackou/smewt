#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
# Copyright (c) 2008 Ricard Marxer
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

from smewt.guessers.guesser import Guesser
from smewt import config

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

import sys
import re
from urllib import *

from media.series.serieobject import EpisodeObject

class EpGuides(Guesser):
    def __init__(self):
        super(EpGuides, self).__init__()
        
        if config.test_localweb:
            self.connect(self, SIGNAL('gotSerie'),
                         self.getEpisodeList)
            self.getGoogleResult(True)
            return
        
        # urllib doesn't cut it against google, better use webkit here...
        #return urlopen('http://www.google.com/search', urlencode({'q': name})).read()
        self.googleResult = None
        self.queryPage = QWebView()

        self.connect(self.queryPage, SIGNAL('loadFinished(bool)'),
                     self.getGoogleResult)

        self.connect(self, SIGNAL('gotSerie'),
                     self.getEpisodeList)

    def guess(self, mediaObject):
        if mediaObject.typename == 'Episode':
            if mediaObject['serie'] is not None:
                print 'Guesser: EpGuides - looking for serie', mediaObject['serie']
                query = 'allintitle: site:epguides.com ' + mediaObject['serie']
                url = QUrl.fromEncoded('http://www.google.com/search?' + urlencode({'q': query}))
                self.queryPage.load(url)
                return
            else:
                print 'Guesser: Does not contain ''serie'' metadata. Try when it has some info.'
        else:
            print 'Guesser: Not an EpisodeObject.  Cannot guess.'
            
        return super(EpGuides, self).guess(mediaObject)

    def getGoogleResult(self, ok):
        print 'Guesser: EpGuides - got result url from google ok =', ok
        if config.test_localweb:
            self.googleResult = open(config.local_epguides_googleresult).read().decode('utf-8')
        else:
            self.googleResult = unicode(self.queryPage.page().mainFrame().toHtml())

        self.serieUrl = re.compile('<h2 class.*?a href=\"(.*?)\" class').findall(self.googleResult)[0]
        print 'Found:', self.serieUrl
        print '*'*100
        self.emit(SIGNAL('gotSerie'), self.serieUrl)

    def getEpisodeList(self, url):
        print 'getting episode list'
        if config.test_localweb:
            html = open(config.local_epguides_episodelist).read()
        else:
            html = urlopen(url).read()
        print 'Guesser: EpGuides - got episodes list from epguides'
        #print html

        # extract serie name
        serieName = re.compile('<h1>.*?>(.*?)</a></h1>').findall(html)[0]
        #print 'found seriename:', serieName

        # extract episode table text
        tableText = re.compile('<pre>(.*?)</pre>', re.DOTALL).findall(html)[0]

        # try to get the info for each episode
        episodes = []
        for line in tableText.split('\n'):
            rexp = '[0-9]+\. *(?P<season>[0-9]+)- *(?P<episodeNumber>[0-9]+) *(?P<prodNumber>[^ ]+) *'
            rexp += '(?P<originalAirDate>[0-9]+ ... [0-9]+)?.*href="(?P<epguideUrl>.*?)">(?P<title>.*)</a>'
            result = re.compile(rexp).search(line)
            if result:
                newep = EpisodeObject.fromDict(result.groupdict())
                newep['serie'] = serieName

                for prop in newep.properties:
                    newep.confidence[prop] = 0.9
                
                episodes.append(newep)

        #self.episodes = episodes
        self.emit(SIGNAL('guessFinished'), episodes)

    def exitNow(self):
        print 'exiting'
        QCoreApplication.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    guesser = EpGuides()
    mediaObject = EpisodeObject.fromDict({'serie': sys.argv[1], 'title': sys.argv[2]})
    print mediaObject.typename
    def printResults(guesses):
        for guess in guesses:
            print guess.properties

    app.connect(guesser, SIGNAL('guessFinished'), printResults)
    
    guesser.guess(mediaObject)    
    
    app.exec_()
