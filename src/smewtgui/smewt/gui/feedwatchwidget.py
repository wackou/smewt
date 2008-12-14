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

from smewt import SmewtException, Collection, SmewtUrl, EventServer
from PyQt4.QtCore import SIGNAL, QVariant, QProcess, QSettings, QThread
from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QListWidget, QListView, QInputDialog, QLineEdit, QAbstractItemView, QLabel, QMessageBox
from smewt.plugins.amulefeedwatcher import AmuleFeedWatcher
import logging


class CheckThread(QThread):
    def __init__(self, parent, feedList):
        super(CheckThread, self).__init__(parent)
        self.feedList = feedList

    def run(self):
        self.feedList.checkAllFeeds()


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

        self.amulePwdEdit = QLineEdit(QSettings().value('amulePwd').toString())
        self.connect(self.amulePwdEdit, SIGNAL('editingFinished()'),
                     self.saveAmulePwd)

        buttons = QHBoxLayout()
        buttons.addWidget(addFeedButton)
        buttons.addWidget(removeFeedButton)
        buttons.addStretch()
        buttons.addWidget(checkNowButton)
        buttons.addWidget(QLabel('Amule password:'))
        buttons.addWidget(self.amulePwdEdit)

        # main layout
        layout = QVBoxLayout()
        self.feedView = QListView()
        self.feedView.setModel(self.feedList)
        layout.addWidget(self.feedView)

        layout.addLayout(buttons)

        eventView = QListView()
        eventView.setSelectionMode(QAbstractItemView.NoSelection)
        eventView.setModel(self.eventList)
        layout.addWidget(eventView)

        self.setLayout(layout)

    def saveAmulePwd(self):
        QSettings().setValue('amulePwd', QVariant(self.amulePwdEdit.text()))

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
