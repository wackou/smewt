#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebView,  QWebPage
import sys
import dbus
from media.series import view
from gui.querywidget import QueryWidget
from gui.resultwidget import ResultWidget
from smewt import config



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
        #self.connect(self.queryTab, SIGNAL('newFolderMetadata'),
        #             self.newFolderMetadata)

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
    """
    def newFolderMetadata(self):
        md = self.queryTab.collection.medias
        webview = QWebView()
        webview.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.connect(webview,  SIGNAL('linkClicked(const QUrl&)'),
                     self.linkClicked)
        webview.page().mainFrame().setHtml(view.render(md))
        self.mainWidget.addTab(webview, 'folder view')
        self.mainWidget.setCurrentIndex(self.mainWidget.count() - 1)
    """



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("DigitalGaia")
    app.setOrganizationDomain("smewt.com")
    app.setApplicationName("Smewg")
    sgui = SmewtGui()
    sgui.show()
    app.exec_()
