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

from smewt.guessers.guesser import Guesser
from smewt import config

from PyQt4.QtCore import SIGNAL, QObject, QUrl
from PyQt4.QtWebKit import QWebView

import sys
import re
from urllib import urlopen,  urlencode

from smewt.media.series import Episode

class EpGuideQuerier(QObject):
    episodeLists = {}

    def __init__(self, mediaObject):
        super(EpGuideQuerier, self).__init__()

        self.mediaObject = mediaObject

        self.connect(self, SIGNAL('gotEpisodeList'),
                     self.makeGuesses)

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


    def query(self):
        if self.episodeLists.has_key(self.mediaObject['serie']):
            self.emit(SIGNAL('gotEpisodeList'))
        else:
            print 'Guesser: EpGuides - looking for serie', self.mediaObject['serie']
            query = 'allintitle: site:epguides.com ' + self.mediaObject['serie']
            url = QUrl.fromEncoded('http://www.google.com/search?' + urlencode({'q': query},  doseq=True))
            self.queryPage.load(url)

    def getGoogleResult(self, ok):
        print 'Guesser: EpGuides - got result url from google ok =', ok
        if config.test_localweb:
            self.googleResult = open(config.local_epguides_googleresult).read().decode('utf-8')
        else:
            self.googleResult = unicode(self.queryPage.page().mainFrame().toHtml())

        matches = re.compile('<h2 class.*?a href=\"(.*?)\" class').findall(self.googleResult)
        if not matches:
            self.episodeLists[self.mediaObject['serie']] = []
            self.emit(SIGNAL('gotEpisodeList'))
            return

        self.serieUrl = matches[0]
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
                # FIXME: surely there is a better way to do this...
                # we get this from the web, assume iso-8859-1
                d = result.groupdict()
                for name, value in d.items():
                    if type(value) == str:
                        d[name] = value.decode('iso-8859-1')
                newep = Episode.fromDict(d)
                newep['serie'] = unicode(serieName)

                episodes.append(newep)

        self.episodeLists[self.mediaObject['serie']] = episodes
        self.emit(SIGNAL('gotEpisodeList'))
        #self.episodes = episodes

    def makeGuesses(self):
        import copy
        guesses = []
        episodeList = self.episodeLists[self.mediaObject['serie']]
        for newep in episodeList:
            # Calculate the confidence of the episode
            # We compare how many matching properties it has with the input mediaObject
            # we weight the matching by the confidence of each property
            commonProps = set(newep.properties) & set(self.mediaObject.properties)
            episodeConfidence = 0.0
            for prop in commonProps:
                if newep[prop] == self.mediaObject[prop]:
                    #episodeConfidence += newep.confidence.get(prop, 1.0) * self.mediaObject.confidence.get(prop, 1.0)
                    #try:
                    episodeConfidence += 1.0
                    #except

            episodeConfidence /= float(len(commonProps))
            #print 'Guesser: episode confidence == %.3f' % episodeConfidence
            #print newep

            guess = Episode()
            guess.confidence = episodeConfidence
            for prop in newep.properties:
                guess[prop] = newep[prop]
                #guess.confidence[prop] = 0.9 * episodeConfidence

            guesses.append(guess)

        self.emit(SIGNAL('guessFinished'), self.mediaObject, guesses)

class EpGuides(Guesser):
    def __init__(self):
        super(EpGuides, self).__init__()

    def guess(self, query):
        self.mediaObjectQueries = {}
        self.query = query
        self.resultMetadata = query.metadata
        mediaObject = query.media[0]
        if mediaObject.type() == 'video':
            for md in list(query.metadata):
                if md['serie']:
                    self.mediaObjectQueries[md] = EpGuideQuerier(md)
                    self.connect(self.mediaObjectQueries[md], SIGNAL('guessFinished'),
                                 self.queryFinished)
                else:
                    print 'Guesser: Does not contain ''serie'' metadata. Try when it has some info.'
                    #self.resultMediaObjects.append(mediaObject)
        else:
            print 'Guesser: Not an EpisodeObject.  Cannot guess.'
            #self.resultMediaObjects.append(mediaObject)

        for querier in self.mediaObjectQueries.values():
            querier.query()

    def queryFinished(self, metadata, guesses):
        self.mediaObjectQueries.pop(metadata)
        self.resultMetadata += guesses

        if len(self.mediaObjectQueries) == 0:
            self.emit(SIGNAL('guessFinished'), self.query)

    def exitNow(self):
        print 'exiting'
        QCoreApplication.exit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    guesser = EpGuides()
    mediaObjects = [EpisodeObject.fromDict({'serie': sys.argv[1],
                                            'title': sys.argv[2],
                                            'episodeNumber': sys.argv[3]})]
    def printResults(guesses):
        for guess in guesses:
            print guess

    app.connect(guesser, SIGNAL('guessFinished'), printResults)

    guesser.guess(mediaObjects)

    app.exec_()
