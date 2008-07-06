#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
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

import os
import sys
from urllib import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import time
import re
import config
from media.series.serieobject import EpisodeObject

class WebPlugin:
    pass


class WebPluginEpGuides(QObject):
    def __init__(self):
        super(WebPluginEpGuides, self).__init__()

    def singleSerieUrl(self, name):
        if config.test_localweb:
            self.connect(self, SIGNAL('gotSerie'),
                         self.getEpisodeList)
            self.getGoogleResult(True)
            return
        # urllib doesn't cut it against google, better use webkit here...
        #return urlopen('http://www.google.com/search', urlencode({'q': name})).read()
        self.googleResult = None
        self.queryPage = QWebView()
        print 'WebPlugin: EpGuides - looking for serie', name
        query = 'allintitle: site:epguides.com ' + name
        url = QUrl.fromEncoded('http://www.google.com/search?' + urlencode({'q': query}))
        self.connect(self.queryPage, SIGNAL('loadFinished(bool)'),
                     self.getGoogleResult)
        self.queryPage.load(url)

        self.connect(self, SIGNAL('gotSerie'),
                     self.getEpisodeList)


    def getGoogleResult(self, ok):
        print 'WebPlugin: EpGuides - got result url from google ok =', ok
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
        print 'WebPlugin: EpGuides - got episodes list from epguides'
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

        self.episodes = episodes
        self.emit(SIGNAL('done'))
        #self.exitNow()

    def exitNow(self):
        print 'exiting'
        QCoreApplication.exit()

def test(query):
    #a = QApplication(sys.argv)
    w = WebPluginEpGuides()
    w.singleSerieUrl(query)
    #a.exec_()
    #print 'je suis de retour'

if __name__ == '__main__':
    test(sys.argv[1])
