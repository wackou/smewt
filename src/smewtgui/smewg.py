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

from PyQt4.QtGui import QApplication, QMainWindow,  QWidget,  QStatusBar,  QProgressBar,  QHBoxLayout, QTabWidget, QIcon, QSystemTrayIcon, QAction, QMenu
from PyQt4.QtCore import SIGNAL
import sys
from smewt.gui import MainWidget, FeedWatchWidget


class StatusWidget(QWidget):
    def __init__(self):
        super(QWidget,  self).__init__()

        layout = QHBoxLayout()
        layout.addStretch()

        self.progressBar = QProgressBar()

        layout.addWidget(self.progressBar)

        self.setLayout(layout)
        return

class SmewtGui(QMainWindow):

    def __init__(self):
        super(SmewtGui, self).__init__()
        self.setWindowTitle('Smewg - An Ordinary Smewt Gui')
        self.mainWidget = MainWidget()
        self.feedWatchWidget = FeedWatchWidget()

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.mainWidget, 'Media')
        self.tabWidget.addTab(self.feedWatchWidget, 'Feed Watcher')

        self.setCentralWidget(self.tabWidget)

        self.statusWidget = StatusWidget()
        self.statusBar().addPermanentWidget(self.statusWidget)

        self.connect(self.mainWidget, SIGNAL('progressChanged'), self.progressChanged)

        self.icon = QIcon('smewt/icons/nepomuk.png')
        self.setWindowIcon(self.icon)

        self.createTrayIcon()

    def createTrayIcon(self):
        self.quitAction = QAction('Quit', self)
        self.connect(self.quitAction, SIGNAL('triggered()'),
                     QApplication.instance().quit)

        trayMenu = QMenu(self)
        trayMenu.addAction(self.quitAction)


        self.trayIcon = QSystemTrayIcon(self.icon, self)
        self.trayIcon.setContextMenu(trayMenu)
        self.trayIcon.setVisible(True)

        self.connect(self.trayIcon, SIGNAL('activated(QSystemTrayIcon::ActivationReason)'),
                     self.iconActivated)


    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.Trigger or reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.setVisible(False)
            else:
                self.setVisible(True)

    def closeEvent(self, event):
        self.hide()
        event.ignore()

    def progressChanged(self,  tagged,  total):
        if total == 0:
            self.statusWidget.progressBar.reset()
        else:
            self.statusWidget.progressBar.setMaximum(total)
            self.statusWidget.progressBar.setValue(tagged)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("DigitalGaia")
    app.setOrganizationDomain("smewt.com")
    app.setApplicationName("Smewg")

    from smewt.base import cache
    cache.load('/tmp/smewt.cache')

    c = cache.globalCache

    sgui = SmewtGui()
    sgui.show()
    app.exec_()

    print 'writing cache to disk...'
    cache.save('/tmp/smewt.cache')
    print 'exiting'
    sys.exit() # why is this necessary when running from eric?
