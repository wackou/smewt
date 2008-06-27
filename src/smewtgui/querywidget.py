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

    def newSearch(self):
        print 'emitting newSearch'
        self.emit(SIGNAL('newSearch'), self.searchBox.text())

    def renderTemplate(self):
        self.emit(SIGNAL('renderTemplate'), self.templates.currentText())

    def setPredefinedResults(self, resultSetName):
        results = predefinedResultSets[str(resultSetName)]
        self.resultTable.setResults(results[0], results[1:])