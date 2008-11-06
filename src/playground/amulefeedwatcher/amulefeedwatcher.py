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
from PyQt4.QtCore import QSettings, QVariant

organizationName = 'DigitalGaia'
applicationName = 'AmuleFeedWatcher'

def amuleDownload(ed2kLink):
    cmd = [ 'amulecmd', '--password=download', '--command="Add %s"' % ed2kLink ]
    amuleReply = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()
    #print 'amule said:', amuleReply

def feedListToQVariant(feedList):
    return QVariant([ QVariant([ QVariant(f['url']),
                                 QVariant([ QVariant(n) for n in f['lastUpdate'] ])
                                 ]) for f in feedList ])

def variantToFeedList(v):
    result = []
    for f in v.toList():
        feed = {}
        feed['url'] = str(f.toList()[0].toString())
        feed['lastUpdate'] = [ n.toInt()[0] for n in f.toList()[1].toList() ]
        result.append(feed)
    return result

def addFeed(url, lastUpdate = None):
    """Example:
    url = 'http://tvu.org.ru/rss.php?se_id=19934' # South Park season 12
    lastUpdate = [2008, 10, 30, 2, 47, 39, 3, 304, 0]
    addFeed(url, lastUpdate)

    if lastUpdate is not specified, it will assume all episodes have already been downloaded"""

    s = QSettings(organizationName, applicationName)
    feedList = variantToFeedList(s.value('feeds'))

    if url not in [ f['url'] for f in feedList ]:
        if not lastUpdate:
            lastUpdate = list(feedparser.parse(url).entries[0].updated_parsed)

        feedList.append({ 'url': url,
                          'lastUpdate': lastUpdate })


    s.setValue('feeds', feedListToQVariant(feedList))

def removeFeed(url):
    s = QSettings(organizationName, applicationName)
    feedList = variantToFeedList(s.value('feeds'))

    for f in feedList:
        if f['url'] == url:
            feedList.remove(f)

    s.setValue('feeds', feedListToQVariant(feedList))


def downloadNewEpisodes(feed):
    f = feedparser.parse(feed['url'])
    print 'Checking new episodes for:', f.channel.title
    lastUpdate = feed['lastUpdate']

    for ep in f.entries:
        if list(ep.updated_parsed) > feed['lastUpdate']:
            lastUpdate = list(ep.updated_parsed)
            print 'Found new episode:', ep.title
            episodeHtml = urllib2.urlopen(ep.id).read()
            ed2kLink = re.compile('href="(?P<url>ed2k://\|file.*?)">').search(episodeHtml).groups()[0]
            amuleDownload(ed2kLink)

    if lastUpdate == feed['lastUpdate']:
        print 'No new episodes...'
    else:
        feed['lastUpdate'] = lastUpdate


if __name__ == '__main__':
    # read feed list
    s = QSettings(organizationName, applicationName)
    feedList = variantToFeedList(s.value('feeds'))

    for feed in feedList:
        downloadNewEpisodes(feed)

    # write back feed list with lastest update
    s.setValue('feeds', feedListToQVariant(feedList))
