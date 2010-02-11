#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2009 Ricard Marxer <email@ricardmarxer.com>
# Copyright (c) 2009 Nicolas Wack <wackou@gmail.com>
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

import logging
import time, os

from PyQt4.QtCore import QObject, SIGNAL, QVariant, QSettings

from smewt.base import Media, Metadata
from smewt.base import ImportTask, SubtitleTask
from smewt.datamodel import MemoryObjectGraph
from smewt.base.utils import GlobDirectoryWalker
from smewt.taggers import EpisodeTagger, MovieTagger

log = logging.getLogger('smewt.base.localcollection')

class LocalCollection(MemoryObjectGraph):
    '''This class represents a collection of resources in a local machine.  The collection
    is specified by a set of folders.
    This collection also keeps a last scanned datetime for each of the folders.
    '''

    def __init__(self, taskManager, seriesFolders = [], moviesFolders = []):
        super(LocalCollection, self).__init__()

        self.taskManager = taskManager

        self.seriesFolders = dict([(folder, None) for folder in seriesFolders])
        self.seriesRecursive = True

        self.moviesFolders = dict([(folder, None) for folder in moviesFolders])
        self.moviesRecursive = True

        self.seriesFolderTimes = {}
        self.moviesFolderTimes = {}

        self.loadSettings()


    def loadSettings(self):
        settings = QSettings()
        self.seriesFolders, self.seriesRecursive = self.loadSettingsByType('series', settings)
        self.moviesFolders, self.moviesRecursive = self.loadSettingsByType('movies', settings)

    def loadSettingsByType(self, typeName, settings):
        folders = [ os.path.abspath(f) for f in unicode(settings.value('local_collection_%s_folders' % typeName).toString()).split(';')
                    if f != '']

        times = [ float(t) if t != 'None' else None for t in str(settings.value('local_collection_%s_folders_times' % typeName).toString()).split(';')
                  if t != '' ]

        if len(folders) != len(times):
            # All or some scan times are missing
            times = [ None ] * len(folders)

        folders = dict([(folder, time) for folder, time in zip(folders, times)])
        recursive = settings.value('local_collection_%s_folders_recursive' % typeName, QVariant(True)).toBool()

        return folders, recursive

    def saveSettings(self):
        settings = QSettings()
        self.saveSettingsByType('series', self.seriesFolders, self.seriesRecursive, settings)
        self.saveSettingsByType('movies', self.moviesFolders, self.moviesRecursive, settings)


    def saveSettingsByType(self, typeName, foldersDict, recursive, settings):
        if not foldersDict:
            return

        folders, times = zip(*(foldersDict.items()))

        self.settings.setValue('local_collection_%s_folders' % typeName, QVariant(';'.join(folders)))
        self.settings.setValue('local_collection_%s_folders_times' % typeName, QVariant(';'.join([str(t)
                                                                                                  for t in times])))
        self.settings.setValue('local_collection_%s_folders_recursive' % typeName, QVariant(recursive))


    def __iadd__(self, obj):
        super(LocalCollection, self).__iadd__(obj)
        #self.emit updated

    def addObject(self, obj):
        super(LocalCollection, self).addObject(obj)
        #self.emit updated

    def removeNotPresent(self):
        # Remove the nodes that are not in one of the folders anymore
        def mediasOfUnselectedFolders( media, folders, recursive ):
            for folder in folders:
                if recursive:
                    if os.path.abspath(media.filename).startswith(folder):
                        return False
                else:
                    if os.path.basename(os.path.abspath(media.filename)) == os.path.basename(folder):
                        return False

            return True


        mediasNotInSeries = self.findAll(type = Media,
                                         select = lambda x: mediasOfUnselectedFolders(x, self.seriesFolders.keys(), self.seriesRecursive))

        mediasNotInMovies = self.findAll(type = Media,
                                         select = lambda x: mediasOfUnselectedFolders(x, self.moviesFolders.keys(), self.moviesRecursive))

        self.nodes -= (set(mediasNotInSeries) & set(mediasNotInMovies))

    def modifiedFolders(self, folder, lastScanned, recursive):
        """Return the folders that have been modified since lastScanned.
        """
        result = []

        if lastScanned is None or lastScanned < os.path.getmtime(folder):
            result.append(folder)

        elif recursive:
            for f in GlobDirectoryWalker(folder, recursive = recursive):
                if os.path.isdir(f) and lastScanned < os.path.getmtime(f):
                    result.append(f)

        return result


    def reimportFolders(self, rescan = False):
        # Import those folders whose modified time
        # is larger than the last scan time
        for folder, lastScanned in self.seriesFolders.items():
            # It's possible that
            # it is a removeable drive
            if not os.path.isdir(folder):
                continue

            if rescan:
                self.importSeriesFolder(folder)
            else:
                modifiedFolders = self.modifiedFolders(folder, lastScanned, self.seriesRecursive)

                for modifiedFolder in modifiedFolders:
                    self.importSeriesFolder(modifiedFolder)

        # Import those folders whose modified time
        # is larger than the last scan time
        for folder, lastScanned in self.moviesFolders.items():
            # It's very possible that
            # it is a removeable drive
            if not os.path.isdir(folder):
                continue

            if rescan:
                self.importMoviesFolder(folder)
            else:
                modifiedFolders = self.modifiedFolders(folder, lastScanned, self.moviesRecursive)

                for modifiedFolder in modifiedFolders:
                    self.importMoviesFolder(modifiedFolder)

    def rescan(self):
        # Reload settings in case they have changed
        self.loadSettings()

        # Remove those media that are not in one of the selected folders
        self.removeNotPresent()

        # Reimport all the folders
        self.reimportFolders( rescan = True )

        # We save the settings of the folders we have imported
        self.saveSettings()

    def update(self):
        # Reload settings in case they have changed
        self.loadSettings()

        # Remove those media that are not in one of the selected folders
        self.removeNotPresent()

        # Reimport only the folders that have changed
        self.reimportFolders( rescan = False )

        # We save the settings of the folders we have imported
        self.saveSettings()

    def importSeriesFolder(self, folder):
        # Set the last time the folder was scanned
        self.seriesFolderTimes[folder] = time.mktime(time.localtime())

        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]

        for filename in GlobDirectoryWalker(folder, filetypes, recursive = self.recursive):
            importTask = ImportTask(self, EpisodeTagger, filename)
            #self.connect(importTask, SIGNAL('taskFinished'), self.seriesTaskFinished)

            self.taskManager.add(importTask)


    def importMoviesFolder(self, folder):
        # Set now as the last time the folder was scanned
        # we set it in a different dictionary in case the task
        # does not finish
        self.moviesFolderTimes[folder] = time.mktime(time.localtime())

        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]

        for filename in GlobDirectoryWalker(folder, filetypes, recursive = self.recursive):
            importTask = ImportTask(folder, MovieTagger, filename)
            #self.connect(importTask, SIGNAL('taskFinished'), self.moviesTaskFinished)

            self.taskManager.add(importTask)


    def seriesTaskFinished(self, task):
        # Since the task may have been of a subfolder we must find
        # the selected folder to which it belonged
        selectedFolder = [folder for folder in self.seriesFolders if task.folder.startswith(folder)]
        selectedFolder.sort(key = lambda x: len(x))

        # Set the last time the folder was scanned
        self.seriesFolders[selectedFolder[0]] = self.seriesFolderTimes[task.folder]

        # We save the settings of the folders we have imported
        self.saveSettings()

    def moviesTaskFinished(self, task):
        # Since the task may have been of a subfolder we must find
        # the selected folder to which it belonged
        selectedFolder = [folder for folder in self.moviesFolders if task.folder.startswith(folder)]
        selectedFolder.sort(key = lambda x: len(x))

        # Set the last time the folder was scanned
        self.moviesFolders[selectedFolder[0]] = self.moviesFolderTimes[task.folder]

        # We save the settings of the folders we have imported
        self.saveSettings()

    def mergeCollection(self, newData):
        self += newData
