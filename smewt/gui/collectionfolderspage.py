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

from smewt.base import utils
from dirselector import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import sys
import logging

log = logging.getLogger('smewt.gui.collectionsfolderpage')

DEFAULT_WIDTH, DEFAULT_HEIGHT = 500, 600

class CollectionFoldersPage(QDialog):
    def __init__(self,
                 parent,
                 description,
                 collection,
                 #settingKeyFolders = 'collection_folders',
                 #settingKeyRecursive = 'collection_folders_recursive',
                 ):

        QDialog.__init__(self, parent)

        self.collection = collection

        #    if sys.platform == 'darwin' and not self.folders:
        #        self.folders = [ os.environ['HOME'] + '/Movies' ]

        # remove directories which don't exist to avoid a segfault later
        self.folders = [ folder for folder in collection.folders if os.path.isdir(folder) ]

        try:
            self.recursiveSelection = collection.folders.items()[0]
        except:
            self.recursiveSelection = True

        self.layout = QVBoxLayout()

        self.instructions_label = QLabel(description)
        self.layout.addWidget(self.instructions_label)
        self.dirselector = DirSelector(folders = self.folders, recursiveSelection = self.recursiveSelection)

        log.debug('Checked folders: %s' % self.folders)
        if not self.folders:
            if sys.platform in ('darwin', 'linux2'):
                log.debug('Expanding folder: %s' % os.environ['HOME'])
                self.dirselector.expandPathNode(os.environ['HOME'])

        # if we have any folders in our list, try to expand the DirSelector in a smart way
        elif len(self.folders) == 1:
            dir = utils.parentDirectory(self.folders[0])
            log.info('Expanding folder: %s' % dir)
            self.dirselector.expandPathNode(dir)

        else:
            dir = utils.commonRoot(self.folders)
            log.debug('Expanding folder: %s' % dir)
            self.dirselector.expandPathNode(dir)


        self.connect(self.dirselector, SIGNAL('selectionChanged'), self.selectionChanged)
        self.layout.addWidget(self.dirselector)

        self.button_layout = QHBoxLayout()

        self.ok_button = QPushButton("Ok")
        self.apply_button = QPushButton("Apply")
        self.apply_button.setEnabled(False)
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

        size = QSize(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.resize(size)

    def getFolders(self):
        folders = [ unicode(f) for f in self.dirselector.selectedFolders() ]

        # make sure everything's native
        if sys.platform == 'win32':
            folders = [ f.replace('/', '\\') for f in folders ]

        recursiveSelection = self.dirselector.recursiveSelection()

        return dict((folder, recursiveSelection) for folder in folders)

    def ok(self):
        self.apply()
        self.done(1)

    def apply(self):
        self.collection.setFolders(self.getFolders())

        self.apply_button.setEnabled(False)

    def cancel(self):
        self.done(0)

    def selectionChanged(self):
        originalFolders = set([os.path.abspath(f) for f in self.folders])
        newFolders = set([os.path.abspath(str(f)) for f in self.dirselector.selectedFolders()])
        if originalFolders != newFolders or self.recursiveSelection != self.dirselector.recursiveSelection():
            self.apply_button.setEnabled(True)

        else:
            self.apply_button.setEnabled(False)
