#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2011 Nicolas Wack <wackou@smewt.com>
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

from __future__ import unicode_literals

from smewt.base import utils, Media, ImportTask
from smewt.base.configobject import CollectionSettings
from smewt.base.textutils import u
import json
import os
import logging

log = logging.getLogger(__name__)


class Collection(object):
    """A Collection keeps track of the files in the folders for us. when any changes
    happen there, it creates new import tasks for new files or removes references to
    deleted files."""

    def __init__(self, name, validFiles, mediaTagger, dataGraph, taskManager, folders = {}):
        log.debug('Initializing %s Collection', name)
        # identifies the collection
        self.name = name
        # validFiles is a list of conditions a file should meet to be
        # considered to belong to this collection
        self.validFiles = validFiles
        self.mediaTagger = mediaTagger

        self.graph = dataGraph
        self.taskManager = taskManager

        # folders is a list of (folder name, bool) indicating whether
        # they should be traversed recursively
        self.folders = folders

        self.loadSettings()


    def findOrCreate(self):
        for c in utils.tolist(self.graph.config.get('collections')):
            if c.name == self.name:
                return c
        result = CollectionSettings.fromDict({ 'name': self.name, 'folders': [] }, self.graph)
        self.addToConfig(result)
        return result

    def loadSettings(self):
        c = self.findOrCreate().toDict()
        self.folders = c['folders']

    def addToConfig(self, c):
        if c not in utils.tolist(self.graph.config.get('collections')):
            self.graph.config.append('collections', c)


    def saveSettings(self):
        c = self.findOrCreate()
        c.folders = json.dumps(self.folders)

    def checkIntegrity():
        # TODO: delete files in set(files) - set(dirwalk())
        pass

    def setFolders(self, folders):
        self.folders = folders
        self.saveSettings()

    def addFolder(self):
        self.folders.append(['', True])
        self.saveSettings()

    def deleteFolder(self, index):
        del self.folders[index]
        self.saveSettings()

    def collectionFiles(self):
        for folder, recursive in self.folders:
            for f in utils.dirwalk(folder, self.validFiles, recursive):
                yield f

    def modifiedFiles(self):
        lastModified = dict((f.filename, f.get('lastModified', None)) for f in self.graph.find_all(Media))
        for f in self.collectionFiles():
            # yield a file if we haven't heard of it yet or if it has been modified recently
            if f not in lastModified or os.path.getmtime(f) > lastModified[f]:
                yield f

    def importFiles(self, files):
        for f in files:
            # new import task
            log.info('Import in %s collection: %s' % (u(self.name), u(f)))
            if self.taskManager:
                importTask = ImportTask(self.graph, self.mediaTagger, f)
                self.taskManager.add(importTask)

        # save newly imported files
        self.saveSettings()

    def update(self):
        log.info('Updating %s collection' % self.name)
        self.importFiles(self.modifiedFiles())

    def rescan(self):
        log.info('Rescanning %s collection' % self.name)
        self.importFiles(self.collectionFiles())
