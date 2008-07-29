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
from resultwidget import ResultWidget

predefinedQueries = [ 'select ?p ?q ?r where { ?p ?q ?r } limit 3',
                      'select ?filename where { ?filename rdfs:type xesam:File } limit 10',
                      'select ?filename ?p ?q where { ?filename rdfs:type xesam:File. ?filename ?p ?q } limit 5'
                      ]

predefinedTemplates = [ 'All Series' ]

predefinedResultSets = { 'series1':
                           [ [ 'filename',                  'serie',        'season', 'epnumber', 'title' ],
                             [ 'file:///data/blah/01.avi',  'Black Lagoon', 1,         1,         'Black Lagoon' ],
                             [ 'file:///data/blah/02.avi',  'Black Lagoon', 1,         2,         'Heavenly Gardens' ],
                             [ 'file:///data/blouh/01.avi', 'Noir',         1,         1,         'La vierge aux mains noires' ]
                             ]
                         }


def fillBlanks(d):
    allKeys = set()
    for elem in d.values():
        for key in elem.keys():
            allKeys.add(key)
    for elem in d.values():
        for key in allKeys:
            if key not in elem:
                elem[key] = ''

class QueryWidget(QWidget):
    def __init__(self):
        super(QueryWidget, self).__init__()

        self.searchBox = QLineEdit()

        self.searchButton = QPushButton('Search!')
        self.connect(self.searchButton, SIGNAL('clicked()'),
                     self.newSearch)

        queries = QComboBox()
        queries.addItem('')
        for q in predefinedQueries:
            queries.addItem(q)
            
        self.connect(queries, SIGNAL('currentIndexChanged(const QString&)'),
                     self.searchBox, SLOT('setText(const QString&)'))

        self.templates = QComboBox()
        self.templates.addItem('')
        for t  in predefinedTemplates:
            self.templates.addItem(t)

        renderButton = QPushButton('Render!')
        self.connect(renderButton, SIGNAL('clicked()'),
                     self.renderTemplate)

        resultSets = QComboBox()
        resultSets.addItem('')
        for rs in predefinedResultSets:
            resultSets.addItem(rs)
        self.connect(resultSets, SIGNAL('currentIndexChanged(const QString&)'),
                     self.setPredefinedResults)

        collectionLoadButton = QPushButton('Load collection...')
        self.connect(collectionLoadButton, SIGNAL('clicked()'),
                     self.loadCollection)

        collectionSaveButton = QPushButton('Save collection...')
        self.connect(collectionSaveButton, SIGNAL('clicked()'),
                     self.saveCollection)

        folderImportButton = QPushButton('Import folder...')
        self.connect(folderImportButton, SIGNAL('clicked()'),
                     self.importFolder)
        
        self.collection = Collection()
        self.connect(self.collection, SIGNAL('collectionUpdated'),
                     self.refreshCollectionView)

        self.resultTable = ResultWidget()

        self.collectionView = QWebView()

        layout1_1 = QHBoxLayout()
        layout1_1.addWidget(self.searchBox)
        layout1_1.addWidget(self.searchButton)
        layout1_2 = QHBoxLayout()
        layout1_2.addWidget(QLabel('Select predefined query:'))
        layout1_2.addWidget(queries)
        layout1 = QVBoxLayout()
        layout1.addLayout(layout1_1)
        layout1.addLayout(layout1_2)

        layout2_1 = QHBoxLayout()
        layout2_1.addWidget(QLabel('Render with template:'))
        layout2_1.addWidget(self.templates)
        layout2_1.addStretch(1)
        layout2_1.addWidget(renderButton)
        layout2_1.addWidget(folderImportButton)
        layout2_1.addWidget(collectionSaveButton)
        layout2_1.addWidget(collectionLoadButton)
        layout2_2 = QHBoxLayout()
        layout2_2.addWidget(QLabel('Select predefined result sets:'))
        layout2_2.addWidget(resultSets)
        layout2 = QVBoxLayout()
        layout2.addLayout(layout2_1)
        layout2.addLayout(layout2_2)

        layout = QVBoxLayout()

        searchGroupBox = QGroupBox('Soprano DB querying')
        searchGroupBox.setLayout(layout1)
        layout.addWidget(searchGroupBox)

        renderGroupBox = QGroupBox('WebKit rendering')
        renderGroupBox.setLayout(layout2)
        layout.addWidget(renderGroupBox)

        #layout.addWidget(self.resultTable)
        layout.addWidget(self.collectionView)

        self.setLayout(layout)

    def loadCollection(self):
        filename = str(QFileDialog.getOpenFileName(self, 'Select file to load the collection'))

        import cPickle
        self.collection = cPickle.load(open(filename))
        self.refreshCollectionView()

    def saveCollection(self):
        filename = str(QFileDialog.getSaveFileName(self, 'Select file to save the collection'))

        import cPickle
        f = open(filename, 'w')
        cPickle.dump(self.collection, f)
        f.close()


    def importFolder(self):
        filename = str(QFileDialog.getExistingDirectory(self, 'Select directory to import', '/data/Series/Futurama/Season 1',
                                                        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        
        self.collection.importFolder(filename)

    def refreshCollectionView(self):
        metadata = dict([(media.getUniqueKey(), media) for media in self.collection.medias if media is not None])
        self.collectionView.page().mainFrame().setHtml(view.render(metadata))
        #self.emit(SIGNAL('newFolderMetadata'))

    def newSearch(self):
        print 'emitting newSearch'
        self.emit(SIGNAL('newSearch'), self.searchBox.text())

    def renderTemplate(self):
        self.emit(SIGNAL('renderTemplate'), self.templates.currentText())

    def setPredefinedResults(self, resultSetName):
        results = predefinedResultSets[str(resultSetName)]
        self.resultTable.setResults(results[0], results[1:])
