#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
# Copyright (c) 2008 Ricard Marxer
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

from smewt.collection import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from media.series import view
from subprocess import Popen
import os
from os.path import dirname,  join

class QueryWidget(QWidget):
    def __init__(self):
        super(QueryWidget, self).__init__()

        folderImportButton = QPushButton('Import folder...')
        self.connect(folderImportButton, SIGNAL('clicked()'),
                     self.importFolder)

        self.collection = Collection()
        self.connect(self.collection, SIGNAL('collectionUpdated'),
                     self.refreshCollectionView)
        self.connect(self.collection, SIGNAL('collectionUpdated'),
                     self.saveCollection)

        self.collectionView = QWebView()
        self.collectionView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.connect(self.collectionView,  SIGNAL('linkClicked(const QUrl&)'),
                     self.linkClicked)

        layout2_1 = QHBoxLayout()
        layout2_1.addStretch(1)
        layout2_1.addWidget(folderImportButton)
        layout2 = QVBoxLayout()
        layout2.addLayout(layout2_1)

        layout = QVBoxLayout()

        renderGroupBox = QGroupBox('WebKit rendering')
        renderGroupBox.setLayout(layout2)
        layout.addWidget(renderGroupBox)

        #layout.addWidget(self.resultTable)
        layout.addWidget(self.collectionView)

        s = QSettings()
        t = s.value('collection_file').toString()
        if t == '':
            t = join(dirname(unicode(s.fileName())),  'Smewg.collection')
            s.setValue('collection_file',  QVariant(t))
        try:
            self.collection.load(t)
        except:
            # if file is not found, just go on with an empty collection
            pass

        self.setLayout(layout)

    def loadCollection(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))
        self.collection.load(filename)

    def saveCollection(self):
        #filename = str(QFileDialog.getSaveFileName(self, 'Select file to save the collection'))

        filename = unicode(QSettings().value('collection_file').toString())

        self.collection.save(filename)

    def importFolder(self):
        filename = str(QFileDialog.getExistingDirectory(self, 'Select directory to import', '/data/Series/Futurama/Season 1',
                                                            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))

        if filename:
            self.collection.importFolder(filename)

    def refreshCollectionView(self):
        metadata = dict([(media.getUniqueKey(), media) for media in self.collection.medias if media is not None])
        self.collectionView.page().mainFrame().setHtml(view.render(metadata))

    def linkClicked(self,  url):
        print 'clicked on link',  url
        action = 'smplayer'
        # FIXME: subtitles don't appear when lauching smplayer...
        args = [ action,  str(url.toString()) ]
        print 'opening with args =',  args
        pid = Popen(args,  env = os.environ).pid

    def renderTemplate(self):
        self.emit(SIGNAL('renderTemplate'), self.templates.currentText())
