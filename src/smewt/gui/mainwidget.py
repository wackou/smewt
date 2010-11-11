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

from smewt import SmewtException, SmewtUrl, Media, Metadata
from smewt.gui.collectionfolderspage import CollectionFoldersPage
from smewt.media import Series, Episode, Movie
from smewt.base import ImportTask, SubtitleTask, LocalCollection, ActionFactory
from smewt.base.taskmanager import Task, TaskManager
from PyQt4.QtCore import SIGNAL, SLOT, QVariant, QProcess, QSettings, pyqtSignature
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy
from PyQt4.QtWebKit import QWebView, QWebPage
from smewt.media import series, movie, speeddial
import logging
import time
from os.path import join, dirname, splitext
from smewt.taggers import EpisodeTagger, MovieTagger
from smewt.base import SmewtDaemon

log = logging.getLogger('smewt.gui.mainwidget')

minZoomFactor = 0.5
maxZoomFactor = 3.0
stepZoomFactor = 0.1

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        def progressCallback(current, total):
            print 'progress callback: %d out of %d' % (current, total)
            self.progressChanged(current, total)
        # FIXME: uncomment me
        #self.connect(self.taskManager, SIGNAL('progressChanged'), self.progressChanged)

        self.collectionView = QWebView()
        self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        #self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
        self.setZoomFactor(QSettings().value('zoom_factor', QVariant(1.0)).toDouble()[0])
        self.connect(self.collectionView,  SIGNAL('linkClicked(const QUrl&)'),
                     self.linkClicked)

        layout = QVBoxLayout()
        layout.addWidget(self.collectionView)

        self.smewtd = SmewtDaemon(progressCallback = progressCallback)
        #self.collection = LocalCollection( taskManager = self.taskManager, settings = QSettings() )
        #self.connect(self.collection, SIGNAL('updated'),
        #             self.refreshCollectionView)
        #self.connect(self.collection, SIGNAL('updated'),
        #             self.saveCollection)

        #try:
        #    self.collection.load(t)
        #except:
        #    log.warning('Could not load collection %s', t)
        #    raise

        self.setLayout(layout)

        self.history = []
        self.index = 0
        baseUrl = QSettings().value('base_url').toString()
        if baseUrl == '':
            baseUrl = 'smewt://media/speeddial/'
        self.setSmewtUrl(baseUrl)

        self.externalProcess = QProcess()

    def shutdown(self):
        self.saveCollection()

    def setZoomFactor(self, factor):
        self.collectionView.page().mainFrame().setTextSizeMultiplier( factor )

    def zoomIn(self):
        zoomFactor = min(QSettings().value('zoom_factor', QVariant(1.0)).toDouble()[0] + stepZoomFactor, maxZoomFactor )
        QSettings().setValue('zoom_factor', QVariant( zoomFactor ) )

        self.setZoomFactor( zoomFactor )

    def zoomOut(self):
        zoomFactor = max(QSettings().value('zoom_factor', QVariant(1.0)).toDouble()[0] - stepZoomFactor, minZoomFactor)
        QSettings().setValue('zoom_factor', QVariant( zoomFactor ) )

        self.setZoomFactor( zoomFactor )

    def back(self):
        self.setSmewtUrl(None, self.index - 1)

    def forward(self):
        self.setSmewtUrl(None, self.index + 1)

    def speedDial(self):
        self.setSmewtUrl(SmewtUrl('media', 'speeddial/'))

    def setSmewtUrl(self, url, index = None):
        if index is not None:
            self.index = min(max(index, 0), len(self.history)-1)
            self.smewtUrl = self.history[self.index]

        else:
            if not isinstance(url, SmewtUrl):
                url = SmewtUrl(url = url)

            self.smewtUrl = url

            self.history[self.index+1:] = []
            self.history.append(url)
            self.index = len(self.history) - 1

        QSettings().setValue('base_url',  QVariant(unicode(self.smewtUrl)))
        self.refreshCollectionView()

    def quit(self):
        #self.taskManager.abortAll()
        pass

    def loadCollection(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))
        self.collection.load(filename)

    def saveCollection(self):
        #filename = unicode(QSettings().value('collection_file').toString())
        #self.collection.save(filename)

        # FIXME: should not be necessary anymore...
        self.smewtd.saveCollection()

    def updateCollectionSettings(self, result):
        if result == 1:
            self.updateCollection()

    def updateCollection(self):
        self.smewtd.collection.update()

    def rescanCollection(self):
        self.smewtd.collection.rescan()

    def selectSeriesFolders(self):
        d = CollectionFoldersPage(self,
                                  type = 'series',
                                  description = 'Select the folders where your series are.',
                                  collection = self.smewtd.collection)
        d.exec_()

    def selectMoviesFolders(self):
        d = CollectionFoldersPage(self,
                                  type = 'movies',
                                  description = 'Select the folders where your movies are.',
                                  collection = self.smewtd.collection)
        d.exec_()


    def progressChanged(self, tagged, total):
        self.emit(SIGNAL('progressChanged'),  tagged,  total)

    def mergeCollection(self, result):
        self.collection += result

    def refreshCollectionView(self):
        surl = self.smewtUrl

        if surl.mediaType == 'speeddial':
            html = speeddial.view.render(surl, self.smewtd.collection)
            self.collectionView.page().mainFrame().setHtml(html)

        elif surl.mediaType == 'series':
            html = series.view.render(surl, self.smewtd.collection)
            #open('/tmp/smewt.html',  'w').write(html.encode('utf-8'))
            #print html[:4000]
            self.collectionView.page().mainFrame().setHtml(html)

        elif surl.mediaType == 'movie':
            html = movie.view.render(surl,  self.smewtd.collection)
            #open('/tmp/smewt.html',  'w').write(html.encode('utf-8'))
            self.collectionView.page().mainFrame().setHtml(html)
            # insert listener object for checkboxes inside the JS environment
            self.connect(self.collectionView.page().mainFrame(), SIGNAL('javaScriptWindowObjectCleared()'),
                         self.connectJavaScript)

        else:
            raise SmewtException('MainWidget: Invalid media type: %s' % surl.mediaType)

    def connectJavaScript(self):
        self.collectionView.page().mainFrame().addToJavaScriptWindowObject('mainWidget', self)

    @pyqtSignature("QString, bool")
    def updateWatched(self, title, watched):
        self.smewtd.collection.find_one(Movie, title = unicode(title)).watched = watched

    @pyqtSignature("QString, QString, QString")
    def addComment(self, title, author, comment):
        g = self.smewtd.collection
        movie = g.find_one(Movie, title = unicode(title))
        commentObj = g.Comment(metadata = movie,
                               author = unicode(author),
                               date = int(time.time()),
                               text = unicode(comment))

        self.refreshCollectionView()

    def linkClicked(self,  url):
        log.info('clicked on link %s', url)
        url = url.toEncoded()

        if url.startsWith('file://'):
            action = 'smplayer'
            args = [ str(url)[7:] ]
            log.debug('launching %s with args = %s', (action, args))
            self.externalProcess.startDetached(action, args)

        elif url.startsWith('smewt://'):
            surl = SmewtUrl(url = url)
            if surl.mediaType:
                self.setSmewtUrl(surl)

            elif surl.actionType:
                ActionFactory().dispatch(self, surl)

            else:
                # probably feed watcher
                self.emit(SIGNAL('feedwatcher'))

        else:
            pass
