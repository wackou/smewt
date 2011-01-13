#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

import sys, os.path
from collections import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from smewt.base.textutils import toUtf8
from smewt.base import utils

class DirSelector(QWidget):
    def __init__(self, focusDir = QDir.currentPath(), parent = None, folders = [], recursiveSelection = True):
        QWidget.__init__(self)

        self.focusDir = focusDir
        self.model = DirModel()
        self.setSelectedFolders( folders )
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        self.connect(self.model, SIGNAL('selectionChanged'),
                     self.selectionChanged)

        # Hide header and all columns but the dirname
        self.tree.header().hide()
        for i in range(self.model.columnCount()-1):
            self.tree.hideColumn(i+1)

        # Expand the first level if there is only one directory
        # Useful for Linux where / is always the first and only directory
        if self.model.rowCount() == 1:
            currentIndex = self.model.index(0,0)
            self.tree.scrollTo( currentIndex,
                                QAbstractItemView.PositionAtTop )
            self.tree.setCurrentIndex( currentIndex )
            self.tree.expand( currentIndex )

        # Don't allow selection
        self.tree.setSelectionMode(QAbstractItemView.NoSelection)

        self.recursive_checkbox = QCheckBox('Select the folders recursively')
        self.connect(self.recursive_checkbox, SIGNAL('stateChanged(int)'), self.setRecursiveSelection)

        self.recursive_checkbox.setCheckState( Qt.Checked if recursiveSelection else Qt.Unchecked )

        self.formLayout = QVBoxLayout()
        self.formLayout.addWidget(self.tree)
        self.formLayout.addWidget(self.recursive_checkbox)
        self.setLayout(self.formLayout)


    def expandPathNode(self, fullpath):
        spath = utils.splitPath(fullpath)
        for i in range(len(spath)):
            self.tree.expand(self.model.index(os.path.join(*spath[:i+1])))

    def recursiveSelection(self):
        return self.model.recursiveSelection

    def setRecursiveSelection(self, state):
        if state == Qt.Checked:
            self.model.setRecursiveSelection( True )

        elif state == Qt.Unchecked:
            self.model.setRecursiveSelection( False )

        self.selectionChanged()

    def selectionChanged(self):
        self.emit(SIGNAL('selectionChanged'))

    def setSelectedFolders(self, folders = []):
        return self.model.setSelectedFolders(folders = folders)

    def selectedFolders(self):
        return self.model.selectedFolders()


class DirModel(QFileSystemModel):

    def __init__(self, parent = None, recursiveSelection = False):
        QFileSystemModel.__init__(self, parent)
        self.setRootPath('/')
        self.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
        self.recursiveSelection = recursiveSelection
        self.clearSelectedFolders()

    def recursiveSelection(self):
        return self.recursiveSelection

    def setRecursiveSelection(self, recursiveSelection):
        self.recursiveSelection = recursiveSelection
        for folder in self.selectedFolders():
            index = self.index(folder)
            if index.isValid():
                self.childrenDataChanged(index)

            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                self.index(folder),
                self.index(folder))

    def clearSelectedFolders(self):
        self.checkstates = defaultdict( lambda : Qt.Unchecked )

    def setSelectedFolders(self, folders):
        self.clearSelectedFolders()

        for folder in folders:
            index = self.index(folder)
            if index.isValid():
                self.setCheckState( index, Qt.Checked )
            else:
                self.checkstates[folder] = Qt.Checked

    def selectedFolders(self):
        return [ k for k, v in self.checkstates.items() if v == Qt.Checked ]

    def data(self, index, role = Qt.DisplayRole):
        if (role == Qt.CheckStateRole and index.column() == 0):
            if self.checkState(index) == Qt.Checked:
                return QVariant( self.checkState(index) )

            else:
                if self.recursiveSelection:
                    if self.parentChecked( index ):
                        return QVariant( Qt.Checked )

                if self.childChecked( index ):
                    return QVariant( Qt.PartiallyChecked )
                else:
                    return QVariant( Qt.Unchecked )
        return QFileSystemModel.data(self, index, role)

    def childChecked(self, index):
        for checkedKey in self.selectedFolders():
            if toUtf8(checkedKey).startswith( toUtf8(self.key( index )) + '/' ):
                return True

        return False

    def parentChecked(self, index):
        key = self.key( index )
        for checkedKey in [folder for folder in self.selectedFolders() if folder != key ]:
            if toUtf8(key).startswith(toUtf8(checkedKey) + '/'):
                return True

        return False

    def key(self, index):
        return self.fileInfo(index).absoluteFilePath()

    def setCheckState(self, index, state):
        self.checkstates[ self.key(index) ] = state


    def childrenDataChanged(self, index, recursive = False):
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  self.index(0, 0, index),
                  self.index(self.rowCount(index)-1, 0, index))

    def parentDataChanged(self, index, recursive = False):
        if recursive and self.parent( index ).isValid():
                self.parentDataChanged( self.parent( index ), recursive = recursive)
        self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
                  self.parent(index), self.parent(index))

    def checkState(self, index):
        return self.checkstates[ self.key(index) ]

    def setData(self, index, value, role = Qt.EditRole):
        if (role == Qt.CheckStateRole and index.column() == 0):
            state = self.checkState(index)

            if state == Qt.Checked:
                self.setCheckState(index, Qt.Unchecked)

            elif state == Qt.Unchecked:
                self.setCheckState(index, Qt.Checked)

            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            self.parentDataChanged(index, recursive = True)
            if self.recursiveSelection:
                self.childrenDataChanged(index, recursive = True)

            self.emit(SIGNAL("selectionChanged"))
            return True

        self.emit(SIGNAL("selectionChanged"))
        return QFilesystemModel.setData(self, index, value, role)


    def flags(self, index):
        if self.recursiveSelection:
            if self.parentChecked( index ):
                return Qt.NoItemFlags

        return Qt.ItemIsUserCheckable  | Qt.ItemIsEnabled



if __name__ == "__main__":
    app = QApplication(sys.argv)

    form = DirSelector()
    form.setWindowTitle("Test")
    form.show()
    sys.exit(app.exec_())
