#!/usr/bin/env python

import math, random, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import imdb

class Window(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        self.thread = Worker()

        label = QLabel(self.tr("Filename:"))
        self.textBox = QLineEdit()
        self.textBox.setText("Matrix")
        self.startButton = QPushButton(self.tr("&Start"))
        self.viewer = QListWidget()
        
        self.connect(self.thread, SIGNAL("finished()"), self.updateUi)
        self.connect(self.thread, SIGNAL("terminated()"), self.updateUi)
        self.connect(self.thread, SIGNAL("output"), self.addText)
        self.connect(self.startButton, SIGNAL("clicked()"), self.makeQuery)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.textBox, 0, 1)
        layout.addWidget(self.startButton, 0, 2)
        layout.addWidget(self.viewer, 1, 0, 1, 3)
        self.setLayout(layout)
        
        self.setWindowTitle(self.tr("Simple Threading Example"))
        
    def makeQuery(self):
    
        self.textBox.setReadOnly(True)
        self.startButton.setEnabled(False)
        self.viewer.clear()
        self.thread.query(self.textBox.text())

    def addText(self, results):
        for result in results:
            self.viewer.addItem( result )

    def updateUi(self):
    
        self.textBox.setReadOnly(False)
        self.startButton.setEnabled(True)

class Worker(QThread):

    def __init__(self, parent = None):
    
        QThread.__init__(self, parent)
        self.text = ""
        self.exiting = False
        self.imdb = imdb.IMDb()

    def __del__(self):
    
        self.exiting = True
        self.wait()

    def query(self, text):
        self.text = text
        self.start()

    def run(self):
        
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        results = self.imdb.search_movie( self.text )
        results = ['%s -- %s' % (r['kind'], r['title']) for r in results]
        self.emit(SIGNAL("output"), results)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
