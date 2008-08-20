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

class ResultWidget(QTableWidget):
    def __init__(self, headerLabels = [], results = []):
        super(ResultWidget, self).__init__()

        self.setResults(headerLabels, results)

    def setResults(self, headerLabels, results):
        self.setRowCount(len(results))
        self.setColumnCount(len(headerLabels))
        self.setHorizontalHeaderLabels(headerLabels)

        for rowIdx, row in enumerate(results):
            for colIdx, cell in enumerate(row):
                self.setItem(rowIdx, colIdx, QTableWidgetItem(str(cell)))

    def getResults(self):
        headers = []
        for idx in range(self.columnCount()):
            headers.append(unicode(self.horizontalHeaderItem(idx).text()))

        results = []
        for row in range(self.rowCount()):
            r = []
            for col in range(self.columnCount()):
                r.append(unicode(self.item(row, col).text()))
            results.append(r)

        return headers, results
