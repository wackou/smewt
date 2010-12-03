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

from smewt import SmewtException, SmewtUrl, EventServer
from PyQt4.QtCore import SIGNAL, QVariant, QProcess, QThread, QTimer, QString
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QListWidget, QListView, QInputDialog, QLineEdit, QAbstractItemView, QLabel, QMessageBox, QDialog, QListWidget
from smewt.plugins.amulefeedwatcher import AmuleFeedWatcher


class CheckThread(QThread):
    def __init__(self, parent, feedList):
        super(CheckThread, self).__init__(parent)
        self.feedList = feedList

    def run(self):
        self.feedList.checkAllFeeds()

class EpisodeSelector(QDialog):
    def __init__(self, feed):
        super(EpisodeSelector, self).__init__()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(feed['title']))

        self.eplist = QListWidget()
        self.eps = sorted(feed['entries'], key = lambda x: x['updated'])
        selectionIndex = -1
        i = 0
        for ep in self.eps:
            self.eplist.addItem(QString(ep['title']))
            if ep['updated'] == feed['lastUpdate']:
                selectionIndex = i
            i += 1
        self.eplist.setCurrentRow(selectionIndex)

        layout.addWidget(self.eplist)

        cancelButton = QPushButton('Cancel')
        okButton = QPushButton('Set as last episode')
        self.connect(cancelButton, SIGNAL('clicked()'),
                     self.reject)
        self.connect(okButton, SIGNAL('clicked()'),
                     self.acceptLocal)

        buttonsLayout = QHBoxLayout()
        buttonsLayout.addStretch()
        buttonsLayout.addWidget(cancelButton)
        buttonsLayout.addWidget(okButton)

        layout.addLayout(buttonsLayout)

        self.setLayout(layout)

    def acceptLocal(self):
        self.lastUpdate = self.eps[self.eplist.currentRow()]['updated']
        self.accept()



class FeedWatchWidget(QWidget):
    def __init__(self):
        super(FeedWatchWidget, self).__init__()

        self.feedList = AmuleFeedWatcher()
        self.eventList = EventServer.events

        # Control buttons: check now, add feed, remove feed
        checkNowButton = QPushButton('Check feeds now!')
        self.connect(checkNowButton, SIGNAL('clicked()'),
                     self.checkNow)

        addFeedButton = QPushButton('Add feed...')
        self.connect(addFeedButton, SIGNAL('clicked()'),
                     self.addFeed)

        removeFeedButton = QPushButton('Remove feed...')
        self.connect(removeFeedButton, SIGNAL('clicked()'),
                     self.removeFeed)

        buttons = QHBoxLayout()
        buttons.addWidget(addFeedButton)
        buttons.addWidget(removeFeedButton)
        buttons.addStretch()
        buttons.addWidget(checkNowButton)

        # main layout
        layout = QVBoxLayout()
        self.feedView = QListView()
        self.feedView.setModel(self.feedList)
        layout.addWidget(self.feedView)

        self.connect(self.feedView, SIGNAL('doubleClicked(const QModelIndex&)'),
                     self.feedEdit)

        layout.addLayout(buttons)

        self.eventView = QListView()
        self.eventView.setSelectionMode(QAbstractItemView.NoSelection)
        self.eventView.setModel(self.eventList)
        layout.addWidget(self.eventView)

        self.setLayout(layout)

        # check for feeds every 2 hours
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'),
                     self.checkNow)
        self.timer.start(2*60*60*1000)

    def feedEdit(self, index):
        fullFeed = self.feedList.getFullFeedIndex(index.row())
        epSelect = EpisodeSelector(fullFeed)
        if epSelect.exec_() == QDialog.Accepted:
            self.feedList.setLastUpdateIndex(index.row(), epSelect.lastUpdate)

    def checkNow(self):
        # this can last a while, do not block the UI meanwhile
        CheckThread(self, self.feedList).start()

    def addFeed(self):
        result, ok = QInputDialog.getText(self, 'Add feed...', 'Enter the feed url:', QLineEdit.Normal, '')
        if ok and not result.isEmpty():
            try:
                self.feedList.addFeed(result)
            except Exception, e:
                QMessageBox.critical(self, 'Add feed...', 'Error: %s' % str(e))

    def removeFeed(self):
        idx = self.feedView.currentIndex().row()
        if idx >= 0:
            self.feedList.removeFeedIndex(idx)
