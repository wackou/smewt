#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import sys
import dbus
from media.series import view
from gui.querywidget import QueryWidget
from gui.resultwidget import ResultWidget
import config


def connectServer():
    no = dbus.SessionBus().get_object('com.smewt.Smewt', '/Smewtd')
    return dbus.Interface(no, 'com.smewt.Smewt.Smewtd')            


def result2objects(headers, rows):
    result = []
    for row in rows:
        r = {}
        for key, obj in zip(headers, row):
            r[key] = obj
        result.append(r)
    return result

def blouh(ok):
    print 'blouh = ', ok

class SmewtGui(QMainWindow):

    def __init__(self):
        super(SmewtGui, self).__init__()
        self.setWindowTitle('Smewt Gui')

        if config.connect_smewtd:
            self.server = connectServer()

        self.queryTab = QueryWidget()
        self.connect(self.queryTab, SIGNAL('newSearch'),
                     self.newSearch)
        self.connect(self.queryTab, SIGNAL('renderTemplate'),
                     self.renderTemplate)
        self.connect(self.queryTab, SIGNAL('newFolderMetadata'),
                     self.newFolderMetadata)

        self.mainWidget = QTabWidget()
        self.mainWidget.addTab(self.queryTab, 'query')

        self.setCentralWidget(self.mainWidget)

    def newSearch(self, queryString):
        results = self.server.query('', unicode(queryString))
        r = ResultWidget(results[0], results[1:])
        self.queryTab.resultTable.setResults(results[0], results[1:])
        #self.mainWidget.addTab(r, 'query:' + queryString)


    def renderTemplate(self, templateName):
        webview = QWebView()
        headers, rows = self.queryTab.resultTable.getResults()
        print rows
        objs = result2objects(headers, rows)
        print objs
        webview.page().mainFrame().setHtml(view.render(objs))
        self.mainWidget.addTab(webview, 'rendered')
        self.mainWidget.setCurrentIndex(self.mainWidget.count() - 1)

    def newFolderMetadata(self):
        md = self.queryTab.folderMetadata
        webview = QWebView()
        webview.page().mainFrame().setHtml(view.render(md))
        self.mainWidget.addTab(webview, 'folder view')
        self.mainWidget.setCurrentIndex(self.mainWidget.count() - 1)
        


if __name__ == '__main__':    
    app = QApplication(sys.argv)
    sgui = SmewtGui()
    sgui.show()
    app.exec_()
