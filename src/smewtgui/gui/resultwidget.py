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
