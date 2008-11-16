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

from PyQt4.QtGui import QApplication, QMainWindow,  QWidget,  QStatusBar,  QProgressBar,  QHBoxLayout
from PyQt4.QtCore import  SIGNAL
import sys
from smewt.gui import MainWidget


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
        self.setCentralWidget(self.mainWidget )

        self.statusWidget = StatusWidget()
        self.statusBar().addPermanentWidget(self.statusWidget)

        self.connect(self.mainWidget .collection,  SIGNAL('progressChanged'),  self.progressChanged)

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
