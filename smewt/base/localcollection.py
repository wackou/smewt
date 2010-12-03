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
from pygoo import MemoryObjectGraph, ontology

from smewt.base import Media, Metadata
from smewt.base import ImportTask, SubtitleTask
from smewt.base.utils import GlobDirectoryWalker
from smewt.taggers import EpisodeTagger, MovieTagger
import cPickle as pickle

log = logging.getLogger('smewt.base.localcollection')

class LocalCollection(MemoryObjectGraph):
    '''This class represents a collection of resources in a local machine.  The collection
    is specified by a set of folders.
    This collection also keeps a last scanned datetime for each of the folders.
    '''

    def __init__(self, taskManager, settingsFile):
        super(LocalCollection, self).__init__()

        self.taskManager = taskManager
        self.settingsFile = settingsFile

        self.seriesFolders = {}
        self.seriesRecursive = True
        self.seriesFolderTimes = {}

        self.moviesFolders = {}
        self.moviesRecursive = True
        self.moviesFolderTimes = {}

        self.loadSettings()


    def loadSettings(self):
        try:
            self.seriesFolders, self.seriesRecursive, self.moviesFolders, self.moviesRecursive = pickle.load(open(self.settingsFile))
        except IOError, e:
            log.warning(e)

    def saveSettings(self):
        pickle.dump((self.seriesFolders, self.seriesRecursive, self.moviesFolders, self.moviesRecursive), open(self.settingsFile, 'w'))

    def getMoviesSettings(self):
        return self.moviesFolders.keys(), self.moviesRecursive

    def setMoviesFolders(self, folders, recursive):
        newfolders = {}
        for folder in folders:
            # try to keep the last scanned time (if any)
            newfolders[folder] = self.moviesFolders[folder] if folder in self.moviesFolders else None
        self.moviesFolders = newfolders
        self.moviesRecursive = recursive
        self.saveSettings()
        self.update()

    def getSeriesSettings(self):
        return self.seriesFolders.keys(), self.seriesRecursive

    def setSeriesFolders(self, folders, recursive):
        newfolders = {}
        for folder in folders:
            # try to keep the last scanned time (if any)
            newfolders[folder] = self.seriesFolders[folder] if folder in self.seriesFolders else None
        self.seriesFolders = newfolders
        self.seriesRecursive = recursive
        self.saveSettings()
        self.update()

    def add_object(self, *args, **kwargs):
        obj = args[0]
        if isinstance(obj, Media):
            self.updateLastScannedTimes([ obj ])
        return super(LocalCollection, self).add_object(*args, **kwargs)

    def removeNotPresent(self):
        # Remove the nodes that are not in one of the folders anymore
        def mediasOfUnselectedFolders(media, folders, recursive):
            for folder in folders:
                if recursive:
                    if os.path.abspath(media.filename).startswith(folder):
                        return False
                else:
                    if os.path.basename(os.path.abspath(media.filename)) == os.path.basename(folder):
                        return False

            return True


        mediasNotInSeries = self.find_all(node_type = Media,
                                         select = lambda x: mediasOfUnselectedFolders(x, self.seriesFolders.keys(), self.seriesRecursive))

        mediasNotInMovies = self.find_all(node_type = Media,
                                         select = lambda x: mediasOfUnselectedFolders(x, self.moviesFolders.keys(), self.moviesRecursive))

        # FIXME: implement me
        #self.nodes -= (set(mediasNotInSeries) & set(mediasNotInMovies))

    def modifiedFolders(self, folder, lastScanned, recursive):
        """Return the folders that have been modified since lastScanned."""
        result = []

        if lastScanned is None or lastScanned < os.path.getmtime(folder):
            result.append(folder)

        elif recursive:
            for f in GlobDirectoryWalker(folder, recursive = recursive):
                if os.path.isdir(f) and lastScanned < os.path.getmtime(f):
                    result.append(f)

        return result


    def reimportFolders(self, rescan):
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
            # It's very possible that it is a removeable drive
            if not os.path.isdir(folder):
                continue

            if rescan:
                self.importMoviesFolder(folder)
            else:
                modifiedFolders = self.modifiedFolders(folder, lastScanned, self.moviesRecursive)

                for modifiedFolder in modifiedFolders:
                    self.importMoviesFolder(modifiedFolder)

    def rescan(self):
        # Remove those media that are not in one of the selected folders
        self.removeNotPresent()

        # Reimport all the folders
        self.reimportFolders(rescan = True)

    def update(self):
        # Remove those media that are not in one of the selected folders
        self.removeNotPresent()

        # Reimport only the folders that have changed
        self.reimportFolders(rescan = False)

    def importSeriesFolder(self, folder):
        self.seriesFolderTimes[folder] = time.mktime(time.localtime())
        self.importMediaFolder(folder, EpisodeTagger, self.seriesRecursive)

    def importMoviesFolder(self, folder):
        self.moviesFolderTimes[folder] = time.mktime(time.localtime())
        self.importMediaFolder(folder, MovieTagger, self.moviesRecursive)

    def importMediaFolder(self, folder, taggerType, recursive):
        filetypes = [ '*.avi',  '*.ogm',  '*.mkv', '*.sub', '*.srt' ]

        for filename in GlobDirectoryWalker(folder, filetypes, recursive):
            importTask = ImportTask(self, taggerType, filename)
            self.taskManager.add(importTask)

    def updateLastScannedTimes(self, mediaList):
        """Given a list of media that just got inserted into this collection, update the timestamps
        on the containing folders."""
        modified = False
        ontology.import_classes([ 'Movie', 'Series', 'Episode', 'Subtitle' ])

        for media in mediaList:
            if (media.metadata.node.isinstance(Movie) or
                (media.metadata.node.isinstance(Subtitle) and media.metadata.metadata.node.isinstance(Movie))):
                mediaFolders = self.moviesFolders
                folderTimes = self.moviesFolderTimes
            elif (media.metadata.node.isinstance(Episode) or
                  (media.metadata.node.isinstance(Subtitle) and media.metadata.metadata.node.isinstance(Episode))):
                mediaFolders = self.seriesFolders
                folderTimes = self.seriesFolderTimes
            else:
                log.warning("Can't update folder times for media: %s" % media)
                return

            # Since the media may have been of a subfolder we must find
            # the selected folder to which it belonged
            selectedFolder = [ folder for folder in mediaFolders if media.filename.startswith(folder) ]
            selectedFolder = sorted(selectedFolder, key = lambda x: len(x))[0] # sort by path length to get the deepest subdirectory

            # Set the last time the folder was scanned
            try:
                if mediaFolders[selectedFolder] != folderTimes[selectedFolder]:
                    mediaFolders[selectedFolder] = folderTimes[selectedFolder]
                    modified = True

            except KeyError:
                mediaFolders[selectedFolder] = time.mktime(time.localtime())
                modified = True

        if modified:
            self.saveSettings()