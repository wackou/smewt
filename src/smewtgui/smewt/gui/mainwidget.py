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

from smewt import SmewtException, Collection, SmewtUrl
from PyQt4.QtCore import SIGNAL, QVariant, QProcess, QSettings
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt4.QtWebKit import QWebView, QWebPage
from smewt.media.series import view
from bookmarkwidget import BookmarkListWidget
import logging
from os.path import join, dirname, splitext

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        backButton = QPushButton('Back')
        folderImportButton = QPushButton('Import folder...')

        self.connect(backButton, SIGNAL('clicked()'),
                     self.back)
        self.connect(folderImportButton, SIGNAL('clicked()'),
                     self.importFolder)

        self.collection = Collection()
        self.connect(self.collection, SIGNAL('collectionUpdated'),
                     self.refreshCollectionView)
        self.connect(self.collection, SIGNAL('collectionUpdated'),
                     self.saveCollection)

        self.collectionView = QWebView()
        self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        #self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
        self.connect(self.collectionView,  SIGNAL('linkClicked(const QUrl&)'),
                     self.linkClicked)

        toolbar = QHBoxLayout()
        toolbar.addWidget(backButton)
        toolbar.addStretch(1)
        toolbar.addWidget(folderImportButton)

        navigation = QHBoxLayout()

        bookmarks = BookmarkListWidget()
        self.connect(bookmarks,  SIGNAL('selected'),
                     self.setSmewtUrl)
        navigation.addWidget(bookmarks)
        navigation.addWidget(self.collectionView)

        layout = QVBoxLayout()
        layout.addLayout(toolbar)
        layout.addLayout(navigation)

        settings = QSettings()
        t = settings.value('collection_file').toString()
        if t == '':
            t = join(dirname(unicode(settings.fileName())),  'Smewg.collection')
            settings.setValue('collection_file',  QVariant(t))

        try:
            self.collection.load(t)
        except:
            logging.warning('Could not load collection %s', t)
            raise

        self.setLayout(layout)

        self.history = []
        baseUrl = QSettings().value('base_url').toString()
        if baseUrl == '':
            baseUrl = 'smewt://media/series/all'
        self.setSmewtUrl(baseUrl)

        self.externalProcess = QProcess()

    def back(self):
        try:
            self.setSmewtUrl(self.history[-2])
        except IndexError:
            pass

    def setSmewtUrl(self, url):
        if not isinstance(url, SmewtUrl):
            url = SmewtUrl(url)

        self.smewtUrl = url

        try:
            if self.history[-2] == url:
                self.history = self.history[:-2]
        except IndexError:
            pass

        self.history.append(url)

        QSettings().setValue('base_url',  QVariant(str(self.smewtUrl)))
        self.refreshCollectionView()


    def loadCollection(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))
        self.collection.load(filename)

    def saveCollection(self):
        filename = unicode(QSettings().value('collection_file').toString())
        self.collection.save(filename)

    def importFolder(self):
        filename = unicode(QFileDialog.getExistingDirectory(self, 'Select directory to import', '/data/Series/',
                                                            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if filename:
            self.collection.importFolder(filename)

    def refreshCollectionView(self):
        surl = self.smewtUrl

        if surl.mediaType != 'series':
            raise SmewtException('MainWidget: Invalid media type: %s' % surl.mediaType)

        if surl.viewType == 'single':
            metadata = self.collection.filter('series', surl.args[0])
        elif surl.viewType == 'all':
            metadata = dict([(md.uniqueKey(), md) for md in self.collection.metadata ])
        else:
            raise SmewtException('Invalid view type: %s' % surl.viewType)

        html = view.render(surl.viewType,  metadata)

        # display template
        #open('/tmp/smewt.html',  'w').write(html.encode('utf-8'))
        self.collectionView.page().mainFrame().setHtml(html)

    def linkClicked(self,  url):
        logging.info('clicked on link %s', url)
        url = url.toString()

        if url.startsWith('file://'):
            action = 'smplayer'
            args = [ str(url)[7:] ]
            logging.debug('launching %s with args = %s', (action, args))
            self.externalProcess.start(action, args)

        elif url.startsWith('smewt://'):
            surl = SmewtUrl(url)
            if surl.mediaType:
                self.setSmewtUrl(surl)
            elif surl.actionType:
                # TODO: use an ActionFactory to dispatch action to a registered plugin that
                # can provide this type of service, ie: getsubtitles action may be fulfilled
                # by tvsubtitles, opensubtitles, etc...
                if surl.actionType == 'getsubtitles':
                    from smewt.media.subtitle import TVSubtitlesProvider
                    tvsub = TVSubtitlesProvider()
                    languageMap = { 'en': u'English', 'fr': u'Français' }

                    # find episodes which don't have subtitles and get it directly
                    series, language = surl.args
                    files = self.collection.filter('series', series).media
                    videos = [ f for f in files if f.type() == 'video' ]
                    subtitles = [ f for f in files if f.type() == 'subtitle' ]

                    reimport = set()
                    for video in videos:
                        basename = splitext(video.filename)[0]
                        subsBasename = basename + '.' + languageMap[language]
                        foundSubs = [ s for s in subtitles if splitext(s.filename)[0] == subsBasename ]

                        if foundSubs: continue

                        # look which episode metadata is connected to this media file
                        for a, b in self.collection.links:
                            if a is video: episode = b
                            if b is video: episode = a

                        print 'gettings subs for', episode
                        tvsub.downloadSubtitle(subsBasename, episode['series'],
                                               episode['season'], episode['episodeNumber'], language,
                                               video.filename)

                        reimport.add(dirname(video.filename))

                    for dir in reimport:
                        self.collection.importFolder(dir)


        else:
            pass

