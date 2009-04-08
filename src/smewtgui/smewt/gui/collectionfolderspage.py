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
from dirselector import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CollectionFolderPage(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.layout = QVBoxLayout()

        self.instructions_label = QLabel("Select the folders where your series are.")
        self.layout.addWidget(self.instructions_label)

        self.dirselector = DirSelector()
        self.layout.addWidget(self.dirselector)

        self.button_layout = QHBoxLayout()

        self.ok_button = QPushButton("Ok")
        self.apply_button = QPushButton("Apply")
        self.cancel_button = QPushButton("Cancel")

        self.button_layout.addStretch()
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        self.connect(self.ok_button, SIGNAL('clicked()'), self.ok)
        self.connect(self.apply_button, SIGNAL('clicked()'), self.apply)
        self.connect(self.cancel_button, SIGNAL('clicked()'), self.cancel)
        
    def ok(self):
        self.applyFolderSelection()
        self.done(1)

    def apply(self):
        self.applyFolderSelection()

    def cancel(self):
        self.done(1)
        
    def applyFolderSelection(self):
        print 'The following folders have been selected: '
        print '\n'.join([str(f) for f in self.dirselector.selectedFolders()])
        

if __name__ == "__main__":
        app = QApplication(sys.argv)
        
        form = CollectionFolderPage()
        form.setWindowTitle("Test")
        form.show()
        sys.exit(app.exec_())

