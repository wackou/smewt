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

import logging, cPickle
import time, os

from PyQt4.QtCore import QObject, SIGNAL, QVariant

from smewt.base import Media, Metadata
from smewt.base import ImportTask, SubtitleTask
from smewt.base import Graph
from smewt.taggers import EpisodeTagger, MovieTagger

log = logging.getLogger('smewt.base.localcollection')

class LocalCollection(Graph):
    '''This class represents a collection of resources in a local machine.  The collection
    is specified by a set of folders.
    This collection also keeps a last scanned datetime for each of the folders.
    '''

    def __init__(self, seriesFolders = [], moviesFolders = [], taskManager = None, settings = None):
        super(LocalCollection, self).__init__()
        
        self.taskManager = taskManager

        self.seriesFolders = dict([(folder, None) for folder in seriesFolders])
        self.seriesRecursive = True
        
        self.moviesFolders = dict([(folder, None) for folder in moviesFolders])
        self.moviesRecursive = True

        self.seriesFolderTimes = {}
        self.moviesFolderTimes = {}
        
        self.settings = settings
        self.loadSettings()

    def loadSettings(self):
        if self.settings is None:
            return

        self.seriesFolders, self.seriesRecursive = self.loadSettingsByType(typeName = 'series')
        self.moviesFolders, self.moviesRecursive = self.loadSettingsByType(typeName = 'movies')
        
    def loadSettingsByType(self, typeName = 'series'):
        folders = [f for f in str(self.settings.value('local_collection_%s_folders' % typeName).toString()).split(';')
                   if os.path.isdir(f)]
        times = [float(t) if t != 'None' else None for t in str(self.settings.value('local_collection_%s_folders_times' % typeName).toString()).split(';') if t != '']

        if len(folders) != len(times):
            # All or some scan times are missing
            times = [None for folder in folders]

        folders = dict([(folder, time) for folder, time in zip(folders, times)])
        recursive = self.settings.value('local_collection_%s_folders_recursive' % typeName, QVariant(True)).toBool()
        
        return folders, recursive

    def saveSettings(self):
        if self.settings is None:
            return

        self.saveSettingsByType(self.seriesFolders, self.seriesRecursive, typeName = 'series')
        self.saveSettingsByType(self.moviesFolders, self.moviesRecursive, typeName = 'movies')
        
        
    def saveSettingsByType(self, foldersDict, recursive, typeName = 'series'):
        if len(foldersDict) == 0:
            return
            
        folders, times = zip(*(foldersDict.items()))
        
        self.settings.setValue('local_collection_%s_folders' % typeName, QVariant(';'.join(folders)))
        self.settings.setValue('local_collection_%s_folders_times' % typeName, QVariant(';'.join([str(t)
                                                                                                  for t in times])))
        self.settings.setValue('local_collection_%s_folders_recursive' % typeName, QVariant(recursive))

        return

    def update(self):
        # Reload settings in case they have changed
        self.loadSettings()

        # Remove the nodes that are not in one of the folders anymore
        toBeRemoved = self.findAll(Media,
                                   method = lambda x: not any([os.path.abspath(x.filename).startswith(folder)
                                                               for folder in set(self.seriesFolders.keys() + self.moviesFolders.keys())]))

        self.nodes -= set(toBeRemoved)

        # Import those folders whose modified time is larger than the current time
        for folder, lastScanned in self.seriesFolders.items():
            if lastScanned is None or lastScanned < os.path.getmtime(folder):
                self.importSeriesFolder(folder)

        # Import those folders whose modified time is larger than the current time
        for folder, lastScanned in self.moviesFolders.items():
            if lastScanned is None or lastScanned < os.path.getmtime(folder):
                self.importMoviesFolder(folder)

        # We save the settings of the folders we have imported
        self.saveSettings()

    def importSeriesFolder(self, folder):
        # Set the last time the folder was scanned
        self.seriesFolderTimes[folder] = time.mktime(time.localtime())
        
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]

        importTask = ImportTask(folder, EpisodeTagger, filetypes = filetypes,
                                recursive = self.seriesRecursive)
        self.connect(importTask, SIGNAL('foundData'), self.mergeCollection)
        self.connect(importTask, SIGNAL('taskFinished'), self.seriesTaskFinished)
        
        if self.taskManager is not None:
            self.taskManager.add( importTask )

        importTask.start()

    def importMoviesFolder(self, folder):
        # Set now as the last time the folder was scanned
        # we set it in a different dictionary in case the task
        # does not finish
        self.moviesFolderTimes[folder] = time.mktime(time.localtime())
        
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]

        importTask = ImportTask(folder, MovieTagger, filetypes = filetypes,
                                recursive = self.moviesRecursive)
        self.connect(importTask, SIGNAL('foundData'), self.mergeCollection)
        self.connect(importTask, SIGNAL('taskFinished'), self.moviesTaskFinished)
        
        if self.taskManager is not None:
            self.taskManager.add( importTask )

        importTask.start()

    def seriesTaskFinished(self, task):
        # Set the last time the folder was scanned
        self.seriesFolders[task.folder] = self.seriesFolderTimes[task.folder]

        # We save the settings of the folders we have imported
        self.saveSettings()

    def moviesTaskFinished(self, task):
        # Set the last time the folder was scanned
        self.moviesFolders[task.folder] = self.moviesFolderTimes[task.folder]

        # We save the settings of the folders we have imported
        self.saveSettings()

    def mergeCollection(self, newData):
        self += newData
