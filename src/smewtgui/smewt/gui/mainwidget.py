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

from smewt import SmewtException, SmewtUrl, Graph, Media, Metadata
from smewt.media import Series, Episode, Movie
from smewt.importer import Importer
from PyQt4.QtCore import SIGNAL, SLOT, QVariant, QProcess, QSettings
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QSizePolicy
from PyQt4.QtWebKit import QWebView, QWebPage
from smewt.media import series, movie
from bookmarkwidget import BookmarkListWidget
import logging
from os.path import join, dirname, splitext
from smewt.taggers import EpisodeTagger, MovieTagger

log = logging.getLogger('smewt.gui.mainwidget')

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        backButton = QPushButton('Back')
        folderImportButton = QPushButton('Import series folder...')
        movieFolderImportButton = QPushButton('Import movie folder...')

        self.connect(backButton, SIGNAL('clicked()'),
                     self.back)
        self.connect(folderImportButton, SIGNAL('clicked()'),
                     self.importSeriesFolder)
        self.connect(movieFolderImportButton, SIGNAL('clicked()'),
                     self.importMovieFolder)

        self.collection = Graph()
        self.connect(self.collection, SIGNAL('updated'),
                     self.refreshCollectionView)
        self.connect(self.collection, SIGNAL('updated'),
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
        toolbar.addWidget(movieFolderImportButton)

        navigation = QHBoxLayout()

        bookmarks = BookmarkListWidget()
        bookmarks.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
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
            log.warning('Could not load collection %s', t)
            raise

        self.setLayout(layout)

        self.history = []
        baseUrl = QSettings().value('base_url').toString()
        if baseUrl == '':
            baseUrl = 'smewt://media/series/all'
        self.setSmewtUrl(baseUrl)

        self.externalProcess = QProcess()
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]

        self.importer = Importer(filetypes = filetypes)
        self.connect(self.importer, SIGNAL('importFinished'), self.mergeCollection)
        self.connect(self.importer, SIGNAL('progressChanged'), self.progressChanged)
        self.connect(self.importer, SIGNAL('foundData'), self.mergeCollection)
        self.connect(self, SIGNAL('importFolder'), self.importer.importFolder)
        self.importer.start()

    def back(self):
        try:
            self.setSmewtUrl(self.history[-2])
        except IndexError:
            pass

    def setSmewtUrl(self, url):
        if not isinstance(url, SmewtUrl):
            url = SmewtUrl(url = url)

        self.smewtUrl = url

        try:
            if self.history[-2] == url:
                self.history = self.history[:-2]
        except IndexError:
            pass

        self.history.append(url)

        QSettings().setValue('base_url',  QVariant(unicode(self.smewtUrl)))
        self.refreshCollectionView()


    def loadCollection(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))
        self.collection.load(filename)

    def saveCollection(self):
        filename = unicode(QSettings().value('collection_file').toString())
        self.collection.save(filename)

    def importSeriesFolder(self):
        filename = unicode(QFileDialog.getExistingDirectory(self, 'Select directory to import', '/data/Series/',
                                                            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if filename:
            self.importSingleFolder(filename, EpisodeTagger)

    def importMovieFolder(self):
        filename = unicode(QFileDialog.getExistingDirectory(self, 'Select directory to import', '/data/Movies/',
                                                            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if filename:
            self.importSingleFolder(filename, MovieTagger)


    def importSingleFolder(self, path, taggerType):
        self.emit(SIGNAL('importFolder'), path, taggerType)

    def progressChanged(self,  tagged,  total):
        self.emit(SIGNAL('progressChanged'),  tagged,  total)

    def mergeCollection(self, result):
        self.collection += result

    def refreshCollectionView(self):
        surl = self.smewtUrl

        if surl.mediaType == 'series':

            if surl.viewType == 'single':
                # creates a new graph with all the media related to the given series
                episodes = self.collection.findAll(Episode, series = Series(surl.args))
                metadata = Graph()
                for f in self.collection.findAll(Media):
                    if f.metadata in episodes:
                        metadata += f

            elif surl.viewType == 'all':
                metadata = self.collection.findAll(Series)

            else:
                raise SmewtException('Invalid view type: %s' % surl.viewType)

            html = series.view.render(surl.viewType,  metadata)

        elif surl.mediaType == 'movie':

            if surl.viewType == 'single':
                # creates a new graph with all the media related to the given series
                movieMD = self.collection.findAll(Movie, title = surl.args['title'])[0]
                metadata = Graph()
                for f in self.collection.findAll(Media):
                    if f.metadata == movieMD:
                        metadata += f

            elif surl.viewType == 'all':
                metadata = self.collection.findAll(Movie)

            else:
                raise SmewtException('Invalid view type: %s' % surl.viewType)

            html = movie.view.render(surl.viewType,  metadata)

        else:
            raise SmewtException('MainWidget: Invalid media type: %s' % surl.mediaType)

        # display template
        #open('/tmp/smewt.html',  'w').write(html.encode('utf-8'))
        self.collectionView.page().mainFrame().setHtml(html)

    def linkClicked(self,  url):
        log.info('clicked on link %s', url)
        url = url.toEncoded()

        if url.startsWith('file://'):
            action = 'smplayer'
            args = [ str(url)[7:] ]
            log.debug('launching %s with args = %s', (action, args))
            self.externalProcess.start(action, args)

        elif url.startsWith('smewt://'):
            surl = SmewtUrl(url = url)
            if surl.mediaType:
                self.setSmewtUrl(surl)
            elif surl.actionType:
                # TODO: use an ActionFactory to dispatch action to a registered plugin that
                # can provide this type of service, ie: getsubtitles action may be fulfilled
                # by tvsubtitles, opensubtitles, etc...
                if surl.actionType == 'play':
                    action = 'smplayer'
                    args = []
                    nfile = 1
                    while 'filename%d' % nfile in surl.args:
                        args.append(surl.args['filename%d' % nfile])
                        nfile += 1

                    log.debug('launching %s with args = %s' % (action, str(args)))
                    self.externalProcess.start(action, args)

                if surl.actionType == 'getsubtitles':
                    from smewt.media.subtitle import TVSubtitlesProvider
                    tvsub = TVSubtitlesProvider()
                    languageMap = { 'en': u'English', 'fr': u'Français' }

                    # find episodes which don't have subtitles and get it directly
                    series = surl.args['title']
                    language = surl.args['language']
                    episodes = self.collection.findAll(Metadata, series = Series({ 'title': series }))
                    files = [ media for media in self.collection.nodes
                              if isinstance(media, Media) and media.metadata in episodes ]

                    videos = [ f for f in files if f.type() == 'video' ]
                    subtitles = [ f for f in files if f.type() == 'subtitle' ]

                    reimport = set()
                    for video in videos:
                        basename = splitext(video.filename)[0]
                        subsBasename = basename + '.' + languageMap[language]
                        foundSubs = [ s for s in subtitles if splitext(s.filename)[0] == subsBasename ]

                        if foundSubs: continue

                        episode = video.metadata
                        log.info('MainWidget: trying to download subs for %s' % episode)
                        tvsub.downloadSubtitle(subsBasename, episode['series']['title'],
                                               episode['season'], episode['episodeNumber'], language,
                                               video.filename)

                        reimport.add(dirname(video.filename))

                    for dir in reimport:
                        self.importSingleFolder(dir)


        else:
            pass

