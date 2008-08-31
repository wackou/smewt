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
from smewt import config
from smewt.media.series import view
from smewt.gui import MainWidget

import logging


class SmewtGui(QMainWindow):

    def __init__(self):
        super(SmewtGui, self).__init__()
        self.setWindowTitle('Smewg - An Ordinary Smewt Gui')
        self.setCentralWidget(MainWidget())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setOrganizationName("DigitalGaia")
    app.setOrganizationDomain("smewt.com")
    app.setApplicationName("Smewg")

    sgui = SmewtGui()
    sgui.show()
    app.exec_()
