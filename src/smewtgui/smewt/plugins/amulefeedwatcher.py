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

import feedparser
import urllib2, re
import subprocess
from PyQt4.QtCore import SIGNAL, Qt, QSettings, QVariant, QAbstractListModel
from smewt import SmewtException, EventServer

class AmuleFeedWatcher(QAbstractListModel):
    def __init__(self):
        super(AmuleFeedWatcher, self).__init__()
        self.loadFeeds()

    def rowCount(self, parent):
        return len(self.feedList)

    def data(self, index, role = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        return QVariant(self.feedList[index.row()]['title'])

    def feedListToQVariant(self, feedList):
        return QVariant([ QVariant([ QVariant(f['url']),
                                     QVariant(f['title']),
                                     QVariant([ QVariant(n) for n in f['lastUpdate'] ])
                                     ]) for f in feedList ])

    '''
    def toQVariant(self):
        return self.feedListToQVariant(self.feedList)'''

    def variantToFeedList(self, v):
        result = []
        for f in v.toList():
            feed = {}
            feed['url'] = str(f.toList()[0].toString())
            feed['title'] = str(f.toList()[1].toString())
            feed['lastUpdate'] = [ n.toInt()[0] for n in f.toList()[2].toList() ]
            result.append(feed)
        return result

    def loadFeeds(self):
        self.feedList = self.variantToFeedList(QSettings().value('feeds'))

    def saveFeeds(self):
        QSettings().setValue('feeds', self.feedListToQVariant(self.feedList))

    def addFeed(self, url, lastUpdate = None):
        """Example:
        url = 'http://tvu.org.ru/rss.php?se_id=19934' # South Park season 12
        lastUpdate = [2008, 10, 30, 2, 47, 39, 3, 304, 0]
        addFeed(url, lastUpdate)

        if lastUpdate is not specified, it will assume all episodes have already been downloaded"""

        url = str(url)
        if url not in [ f['url'] for f in self.feedList ]:
            try:
                pfeed = feedparser.parse(url)
                feed = { 'url': url,
                         'title': pfeed.channel.title }
            except AttributeError:
                raise SmewtException('Invalid feed!')

            if not lastUpdate:
                lastUpdate = list(pfeed.entries[0].updated_parsed)
            feed['lastUpdate'] = lastUpdate

            self.feedList.append(feed)
            self.saveFeeds()

            # FIXME: we should emit dataChanged here rather than call reset() (same goes for removeFeed)
            self.reset()

    def removeFeed(self, url):
        for f in self.feedList:
            if f['url'] == url:
                self.feedList.remove(f)
                self.saveFeeds()
                self.reset()

    def removeFeedIndex(self, idx):
        self.removeFeed(self.feedList[idx]['url'])


    def amuleDownload(self, ed2kLink, amulePwd):
        cmd = [ 'amulecmd', '--password=%s' % amulePwd, '--command=Add %s' % ed2kLink ]
        amuleReply = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()
        #print 'amule said:', amuleReply
        return '> Operation was successful.' in amuleReply

    def downloadNewEpisodes(self, feed, amulePwd):
        EventServer.publish('Checking new episodes for: %s' % feed['title'])
        f = feedparser.parse(feed['url'])
        lastUpdate = feed['lastUpdate']

        for ep in f.entries:
            if list(ep.updated_parsed) > feed['lastUpdate']:
                EventServer.publish('Found new episode: %s' % ep.title)
                episodeHtml = urllib2.urlopen(ep.id).read()
                ed2kLink = re.compile('href="(?P<url>ed2k://\|file.*?)">').search(episodeHtml).groups()[0]
                if self.amuleDownload(ed2kLink, amulePwd):
                    EventServer.publish('Successfully sent to aMule!')
                    lastUpdate = list(ep.updated_parsed)
                else:
                    EventServer.publish('Error while sending to aMule. Will try again next time...')

        if lastUpdate == feed['lastUpdate']:
            EventServer.publish('No new episodes...')
        else:
            feed['lastUpdate'] = lastUpdate

    def checkAllFeeds(self):
        amulePwd = str(QSettings().value('amulePwd').toString())
        for feed in self.feedList:
            self.downloadNewEpisodes(feed, amulePwd)

        # write back feed list with latest updates
        self.saveFeeds()
