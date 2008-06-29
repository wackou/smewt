#!/usr/bin/python

import os
import sys
from urllib import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import time
import re

class WebPlugin:
    pass


class WebPluginEpGuides(QObject):
    def __init__(self):
        super(WebPluginEpGuides, self).__init__()

    def singleSerieUrl(self, name):
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
        self.googleResult = unicode(self.queryPage.page().mainFrame().toHtml())
        self.serieUrl = re.compile('<h2 class="r"><a href=\"(.*?)\" class="l">').findall(self.googleResult)[0]
        print 'Found:', self.serieUrl
        print '*'*100
        self.emit(SIGNAL('gotSerie'), self.serieUrl)

    def getEpisodeList(self, url):
        html = urlopen(url).read()
        print 'WebPlugin: EpGuides - got episodes list from epguides'

        # extract episode table text
        tableText = re.compile('<pre>(.*?)</pre>', re.DOTALL).findall(html)[0]

        # try to get the info for each episode
        episodes = []
        for line in tableText.split('\n'):
            rexp = '[0-9]+\. *(?P<season>[0-9]+)- *(?P<epNumber>[0-9]+) *(?P<prodNumber>[^ ]+) *'
            rexp += '(?P<originalAirDate>[0-9]+ ... [0-9]+)?.*href="(?P<epguideUrl>.*?)">(?P<title>.*)</a>'
            result = re.compile(rexp).search(line)
            if result:
                episodes.append(result.groupdict())

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