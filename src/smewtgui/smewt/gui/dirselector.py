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

import sys
from collections import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class DirSelector(QWidget):
        def __init__(self, focusDir = QDir.currentPath(), parent=None):
            QWidget.__init__(self)
            
            self.focusDir = focusDir
            self.model = DirModel()
            self.tree = QTreeView()
            self.tree.setModel(self.model)
            
            self.connect(self.model, SIGNAL('selectionChanged'),
                         self.selectionChanged)

            # Hide header and all columns but the dirname
            self.tree.header().hide()
            for i in range(self.model.columnCount()-1):
                self.tree.hideColumn(i+1)

            # Set the focus directory
            currentIndex = self.model.index(self.focusDir)
            self.tree.scrollTo( currentIndex,
                                QAbstractItemView.PositionAtTop )
            self.tree.setCurrentIndex( currentIndex )
            self.tree.expand( currentIndex )

            # Don't allow selection
            self.tree.setSelectionMode( QAbstractItemView.NoSelection )
            
            self.formLayout = QVBoxLayout()
            self.formLayout.addWidget(self.tree)
            self.setLayout(self.formLayout)
            
        def selectionChanged(self):
            self.emit(SIGNAL('selectionChanged'))
                
        def selectedFolders(self):
            return self.model.selectedFolders()
            

class DirModel(QDirModel):

        def __init__(self, parent=None):
            QDirModel.__init__(self, parent)
            self.setFilter( QDir.AllDirs | QDir.NoDotAndDotDot )
            
            self.checkstates = defaultdict( lambda : Qt.Unchecked )
            self.autocheckstates = defaultdict( lambda : Qt.Unchecked )
            self.editable = defaultdict( lambda : True )            

        def selectedFolders(self):
                return [ k for k, v in self.checkstates.items()
                         if v == Qt.Checked ]

        def data(self, index, role = Qt.DisplayRole):
            if (role == Qt.CheckStateRole and index.column() == 0):
                return QVariant( self.autoCheckState(index) )
            
            return QDirModel.data(self, index, role)

        def key(self, index):
            return self.fileInfo(index).absoluteFilePath()

        def setCheckState(self, index, state):
            self.checkstates[ self.key(index) ] = state
            self.autocheckstates[ self.key(index) ] = state
            self.setAutoCheckStateParents( index, Qt.PartiallyChecked if state == Qt.Checked else Qt.Unchecked )
            self.setAutoCheckStateChildren( index, Qt.Checked if state == Qt.Checked else Qt.Unchecked )

        def setAutoCheckStateParents(self, index, state):
            parent = self.parent( index )
            if parent.isValid():
                if state == Qt.Unchecked:
                    # If any of the children are checked or partially checked
                    # we don't continue unchecking
                    for childRow in range( self.rowCount( parent ) ):
                        childIndex = self.index( childRow, 0, parent )
                        if (self.autocheckstates[ self.key( childIndex ) ] == Qt.Checked) or (self.autocheckstates[ self.key( childIndex ) ] == Qt.PartiallyChecked):
                            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), parent, parent)
                            return

                # Set the state of the parent
                self.autocheckstates[ self.key( parent ) ] = state                        
                # Continue propagating check states towards the root tree
                self.setAutoCheckStateParents( parent, state )
                self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), parent, parent)


        def setAutoCheckStateChildren(self, index, state):
            for childRow in range(self.rowCount( index )):
                
                childIndex = self.index(childRow, 0, index)
                
                self.editable[ self.key( childIndex ) ] = (state == Qt.Unchecked)
                
                subState = state
                if state == Qt.Unchecked:
                    subState = self.checkstates[ self.key( childIndex ) ]
                    if subState == Qt.Checked:
                            self.setAutoCheckStateParents( childIndex, Qt.PartiallyChecked )
                    
                self.autocheckstates[ self.key( childIndex ) ] = subState
                self.setAutoCheckStateChildren( childIndex, subState )

            self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.index(0, 0, index), self.index(self.rowCount(index)-1, 0, index))
            
        def autoCheckState(self, index):
            return self.autocheckstates[ self.key( index ) ]

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
                self.emit(SIGNAL("selectionChanged"))
                return True

            self.emit(SIGNAL("selectionChanged"))
            return QDirModel.setData(self, index, value, role)


        def flags(self, index):
            if self.editable[ self.key( index ) ]:
                return Qt.ItemIsUserCheckable  | Qt.ItemIsEnabled
            else:
                return Qt.NoItemFlags



if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        form = DirSelector()
        form.setWindowTitle("Test")
        form.show()
        sys.exit(app.exec_())
