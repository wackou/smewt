#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
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

        folderMetadataSearchButton = QPushButton('Folder search!')
        self.connect(folderMetadataSearchButton, SIGNAL('clicked()'),
                     self.folderMetadataSearch)

        from media.series.tagger import SeriesTagger
        self.st = SeriesTagger()
        self.connect(self.st, SIGNAL('metadataUpdated'),
                     self.newFolderTab)

        self.resultTable = ResultWidget()

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
        layout2_1.addWidget(folderMetadataSearchButton)
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

        layout.addWidget(self.resultTable)

        self.setLayout(layout)

    def folderMetadataSearch(self):
        filename = str(QFileDialog.getExistingDirectory(self, 'Select directory to search', '/data/Series/Futurama/Season 1',
                                                        QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks))
        print 'selected filename', filename


        self.st.tagDirectory(filename)

    def newFolderTab(self):
        # remove the confidence from the metadata set
        '''
        fm = dict(self.st.metadata)
        for filename, md in fm.items():
            for key, (value, confidence) in md.items():
                md[key] = value
        fillBlanks(fm)
        self.folderMetadata = fm.values()
        '''
        self.folderMetadata = self.st.resolveProbabilities()
        self.emit(SIGNAL('newFolderMetadata'))

    def newSearch(self):
        print 'emitting newSearch'
        self.emit(SIGNAL('newSearch'), self.searchBox.text())

    def renderTemplate(self):
        self.emit(SIGNAL('renderTemplate'), self.templates.currentText())

    def setPredefinedResults(self, resultSetName):
        results = predefinedResultSets[str(resultSetName)]
        self.resultTable.setResults(results[0], results[1:])
