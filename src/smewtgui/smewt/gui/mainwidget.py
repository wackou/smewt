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

from smewt import SmewtException, Collection
from PyQt4.QtCore import SIGNAL, QVariant, QProcess, QSettings
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt4.QtWebKit import QWebView, QWebPage
from smewt.media.series import view
from bookmarkwidget import BookmarkListWidget
import logging

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

        t = QSettings().value('collection_file').toString()
        if t == '':
            t = join(dirname(unicode(s.fileName())),  'Smewg.collection')
            s.setValue('collection_file',  QVariant(t))

        try:
            self.collection.load(t)
        except:
            logging.warning('Could not load collection %s', t)
            raise

        self.setLayout(layout)

        s = QSettings()
        self.history = []
        baseUrl = s.value('base_url').toString()
        if baseUrl == '':
            baseUrl = 'smewt://serie/all'
        self.setSmewtUrl(baseUrl)

        self.externalProcess = QProcess()

    def back(self):
        try:
            self.setSmewtUrl(self.history[-2])
        except IndexError:
            pass

    def setSmewtUrl(self, url):
        self.smewtUrl = url

        try:
            if self.history[-2] == url:
                self.history = self.history[:-2]
        except IndexError:
            pass

        self.history.append(url)

        QSettings().setValue('base_url',  QVariant(self.smewtUrl))
        self.refreshCollectionView()


    def loadCollection(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))
        self.collection.load(filename)

    def saveCollection(self):
        filename = unicode(QSettings().value('collection_file').toString())
        self.collection.save(filename)

    def importFolder(self):
        filename = unicode(QFileDialog.getExistingDirectory(self, 'Select directory to import', '/data/Series/Futurama/Season 1',
                                                            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if filename:
            self.collection.importFolder(filename)

    def refreshCollectionView(self):
        surl = SmewtUrl(self.smewtUrl)

        if surl.mediaType != 'serie':
            raise SmewtException('Invalid media type: %s' % surl.mediaType)

        if surl.viewType == 'single':
            metadata = self.collection.filter('serie', args[0])
        elif surl.viewType == 'all':
            metadata = dict([(md.getUniqueKey(), md) for md in self.collection.metadata ])
        else:
            raise SmewtException('Invalid view type: %s' % surl.viewType)

        html = view.render(viewType,  metadata)

        # display template
        #open('/tmp/smewt.html',  'w').write(html.encode('utf-8'))
        self.collectionView.page().mainFrame().setHtml(html)

    def linkClicked(self,  url):
        logging.info('clicked on link %s', url)
        url = url.toString()

        if url.startsWith('file://'):
            action = 'smplayer'
            # FIXME: subtitles don't appear when lauching smplayer...
            args = [ action,  str(url)[7:] ]
            logging.debug('opening with args = %s',  args)
            self.externalProcess.start(action, [str(url)])

        elif url.startsWith('smewt://'):
            self.setSmewtUrl(url)
        else:
            pass

