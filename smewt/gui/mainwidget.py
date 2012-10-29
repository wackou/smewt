#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
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

from smewt import SmewtException, SmewtUrl
from smewt.gui.collectionfolderspage import CollectionFoldersPage
from smewt.media import Series, Movie
from smewt.base import ActionFactory, SmewtDaemon, EventServer
from PyQt4.QtCore import pyqtSignal, SIGNAL, QVariant, QProcess, QSettings, pyqtSignature
from PyQt4.QtGui import QWidget, QVBoxLayout, QFileDialog, QMessageBox, QImage, QPainter, QApplication
from PyQt4.QtWebKit import QWebView, QWebPage
from smewt.media import series, movie, speeddial, tvu, feeds
from guessit.language import Language
import logging
import threading
import time
import sys

log = logging.getLogger('smewt.gui.mainwidget')

minZoomFactor = 0.5
maxZoomFactor = 3.0
stepZoomFactor = 0.1

class MainWidget(QWidget):
    refresh = pyqtSignal()

    def __init__(self):
        super(MainWidget, self).__init__()

        self.collectionView = QWebView()
        self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        #self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
        self.setZoomFactor(QSettings().value('zoom_factor', QVariant(1.0)).toDouble()[0])
        self.connect(self.collectionView,  SIGNAL('linkClicked(const QUrl&)'),
                     self.linkClicked)

        self.refresh.connect(self.refreshCollectionView)
        #self.connect(self, SIGNAL('refresh'), self.refreshCollectionView)

        layout = QVBoxLayout()
        layout.addWidget(self.collectionView)

        self.smewtd = SmewtDaemon()
        self.smewtd.taskManager.progressChanged.connect(self.progressChanged)

        self.setLayout(layout)

        self.history = []
        self.index = 0
        baseUrl = QSettings().value('base_url').toString()
        if baseUrl == '':
            baseUrl = 'smewt://media'
        self.setSmewtUrl(baseUrl)
        # somehow it looks like this refresh is necessary otherwise our main widget doesn't get inserted in the javascript
        self.refreshCollectionView()

        self.externalProcess = QProcess()


    def progressChanged(self, finished, total):
        if total == 0:
            self.refreshCollectionView()

    def quit(self):
        self.smewtd.quit()

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
        self.setSmewtUrl(SmewtUrl('media'))

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
        try:
            self.refreshCollectionView()
        except Exception, e:
            import sys, traceback
            log.warning('Exception:\n%s' % ''.join(traceback.format_exception(*sys.exc_info())))

            # In case of error, return to the home screen
            # FIXME: if we have an error while trying to show the speeddial,
            #        this will make us go into an infinite loop...
            log.warning('Returning to Speed Dial view')
            self.speedDial()

    def loadCollection(self):
        """Debug method."""
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))
        self.collection.load(filename)


    def updateCollectionSettings(self, result):
        if result == 1:
            self.updateCollection()

    def updateCollection(self):
        self.smewtd.updateCollections()

    def rescanCollection(self):
        self.smewtd.rescanCollections()

    def clearCollection(self):
        result = QMessageBox.warning(self,
                                     'Clear collection',
                                     'Are you sure you want to clear the whole collection?\n' +
                                     'Warning: this cannot be undone',
                                     QMessageBox.Ok | QMessageBox.Cancel)

        if result == QMessageBox.Ok:
            self.smewtd.clearDB()
            self.speedDial()

    def selectSeriesFolders(self):
        d = CollectionFoldersPage(self,
                                  description = 'Select the folders where your series are.',
                                  collection = self.smewtd.episodeCollection)
        d.exec_()

    def selectMoviesFolders(self):
        d = CollectionFoldersPage(self,
                                  description = 'Select the folders where your movies are.',
                                  collection = self.smewtd.movieCollection)
        d.exec_()


    def mergeCollection(self, result):
        self.collection += result


    def refreshCollectionView(self):
        surl = self.smewtUrl

        html = self.renderSmewtUrl(self.smewtUrl)
        self.collectionView.page().mainFrame().setHtml(html)

        # FIXME: looks like it isn't working, like for refreshing speeddial after thumbnails have been regenerated
        #self.collectionView.triggerPageAction(QWebPage.ReloadAndBypassCache)

        # insert listener object for objects inside the JS environment that need to
        # interact directly with smewtd or the database (eg: toggle synopsis setting, watched checkboxes, ...)
        self.connect(self.collectionView.page().mainFrame(), SIGNAL('javaScriptWindowObjectCleared()'),
                     self.connectJavaScript)


        #self.takeScreenshot().save("/tmp/smewt_screenshot.png")


    def renderSmewtUrl(self, surl):
        if isinstance(surl, basestring):
            surl = SmewtUrl(url = surl)

        log.debug('Rendering URL: %s' % surl)

        if not surl.mediaType or surl.mediaType == 'speeddial':
            html = speeddial.view.render(surl, self.smewtd.database, self.smewtd)

        elif surl.mediaType == 'series':
            html = series.view.render(surl, self.smewtd.database, self.smewtd)

        elif surl.mediaType == 'movie':
            html = movie.view.render(surl,  self.smewtd.database, self.smewtd)

        elif surl.mediaType == 'tvu':
            html = tvu.view.render(surl, self.smewtd.database, self.smewtd)

        elif surl.mediaType == 'feeds':
            html = feeds.view.render(surl, self.smewtd.database, self.smewtd)

        else:
            raise SmewtException('MainWidget: Invalid media type: %s' % surl.mediaType)

        #open('/tmp/smewt.html',  'w').write(html.encode('utf-8'))
        return html



    def webpageScreenshot(self, html):
        """Take a screenshot of a given html document and return it as a QImage."""
        # see http://www.blogs.uni-osnabrueck.de/rotapken/2008/12/03/create-screenshots-of-a-web-page-using-python-and-qtwebkit/
        size = self.size()
        #size = self.collectionView.page().viewportSize() # seems to be wrongly initialized sometimes...
        webpage = QWebPage()
        webpage.setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        webpage.setViewportSize(size)
        webpage.mainFrame().setHtml(html)

        # need to wait for the different elements to have loaded completely
        if sys.platform == 'linux2':
            while QApplication.hasPendingEvents():
                QApplication.processEvents()
        else:
            QApplication.processEvents()


        image = QImage(size, QImage.Format_ARGB32)
        painter = QPainter(image)
        webpage.mainFrame().render(painter)
        painter.end()

        return image


    def takeScreenshot(self):
        return self.webpageScreenshot(self.collectionView.page().mainFrame().toHtml())


    def connectJavaScript(self):
        self.collectionView.page().mainFrame().addToJavaScriptWindowObject('mainWidget', self)

    @pyqtSignature("QString")
    def setDefaultSubtitleLanguage(self, sublang):
        sublang = str(sublang)
        try:
            lang = Language(sublang, strict=True)
            self.smewtd.database.find_one('Config').defaultSubtitleLanguage = lang.alpha2
        except ValueError:
            pass

    @pyqtSignature("bool")
    def toggleSynopsis(self, synopsis):
        log.info('Set default synopsis state to %s' % synopsis)
        self.smewtd.database.find_one('Config').displaySynopsis = synopsis

    @pyqtSignature("QString, bool")
    def updateWatched(self, title, watched):
        self.smewtd.database.find_one(Movie, title = unicode(title)).watched = watched

    @pyqtSignature("QString, int")
    def lastSeasonWatched(self, series, season):
        self.smewtd.database.find_one(Series, title = unicode(series)).lastSeasonWatched = season

    @pyqtSignature("QString, QString, QString")
    def addComment(self, title, author, comment):
        g = self.smewtd.database
        movie = g.find_one(Movie, title = unicode(title))
        commentObj = g.Comment(metadata = movie,
                               author = unicode(author),
                               date = int(time.time()),
                               text = unicode(comment))

        self.refreshCollectionView()

    @pyqtSignature("QString")
    def feedsForSeries(self, series):
        self.setSmewtUrl('smewt://media/tvu?series=%s' % series)

    @pyqtSignature("QString")
    def subscribeToFeed(self, feedUrl):
        url = unicode(feedUrl)
        self.smewtd.feedWatcher.addFeed(url)
        log.info('Subscribed to feed: %s' % url)
        self.refresh.emit()

    @pyqtSignature("QString")
    def unsubscribeFromFeed(self, feedUrl):
        url = unicode(feedUrl)
        self.smewtd.feedWatcher.removeFeed(url)
        log.info('Unsubscribed from feed: %s' % url)
        self.refresh.emit()

    @pyqtSignature("QString")
    def updateFeed(self, feedUrl):
        url = unicode(feedUrl)
        self.smewtd.feedWatcher.updateFeedUrl(url)
        log.info('Updated info for feed: %s' % url)
        self.refresh.emit()

    @pyqtSignature("QString, int")
    def setLastUpdated(self, feedUrl, index):
        url = unicode(feedUrl)
        self.smewtd.feedWatcher.setLastUpdateUrlIndex(url, index)
        log.info('Updated last entry for feed: %s' % url)
        self.refresh.emit()

    @pyqtSignature("")
    def checkAllFeeds(self):
        def bg_task():
            self.smewtd.feedWatcher.checkAllFeeds()
            self.refresh.emit()
        threading.Thread(target=bg_task).start()

    @pyqtSignature("")
    def clearEventServer(self):
        EventServer.events.clear()
        self.refresh.emit()

    def linkClicked(self,  url):
        log.info('clicked on link %s', unicode(url.toString()))
        url = url.toEncoded()

        if url.startsWith('file://'):
            # FIXME: we should not use this anymore but a SmewtUrl with action = play
            log.warning('Deprecated api: links with file:// ...')
            action = 'smplayer'
            args = [ str(url)[7:] ]
            log.debug('launching %s with args = %s', (action, args))
            self.externalProcess.startDetached(action, args)

        elif url.startsWith('smewt://'):
            surl = SmewtUrl(url = url)
            if surl.urlType == 'media':
                self.setSmewtUrl(surl)

            elif surl.urlType == 'action':
                ActionFactory().dispatch(self, surl)

            else:
                log.warning('Unhandled URL: %s' % url)

        else:
            log.warning('Unhandled URL: %s' % url)
