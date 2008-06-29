#!/usr/bin/python

import os
from os.path import join, split
import sys
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MediaTagger:
    pass

# a metadata probability is a dict from name of property to a list of the possible
# candidates, which are pair of (value, confidence)


# @todo put this inside MediaTagger or not?
def matchAnyRegexp(string, regexps):
    for regexp in regexps:
        result = re.compile(regexp, re.IGNORECASE).search(string)
        if result:
            return result.groupdict()
    return None


def isIncluded(d1, d2):
    for key, value in d1.items():
        try:
            if d2[key] != value:
                return False
        except KeyError:
            return False
    return True


def splitFilename(filename):
    root, path = split(filename)
    result = [ path ]
    while len(root) > 1:
        root, path = split(root)
        result.append(path)
    return result

class SeriesTagger(QObject):
    def __init__(self):
        super(SeriesTagger, self).__init__()
        self.metadata = {}
        
        from webplugin_epguides import WebPluginEpGuides
        self.web = WebPluginEpGuides()
        self.connect(self.web, SIGNAL('done'),
                     self.fetchOnlineMetadata)

    def getAllFilesInDir(self, directory):
        allFiles = []
        print 'get all files', directory[:-1]
        for root, dirs, files in os.walk(directory[:-1]):
            print 'walking', root
            for filename in files:
                allFiles.append(join(root, filename))
        return allFiles

    def addMetadata(self, item, key, value, confidence):
        try:
            filemd = self.metadata[item]
            # possible conflict if some other part of the filename already
            # filled one property: either they're the same (hurray!), or
            # we will have to somehow adjust the confidence of each of these
            # NB: maybe keep all possibilities and resolve them at the end using
            #     a specific solver
            if key in filemd:
                # simple heuristic: keep the one with higher confidence
                # in case of a draw, keep the first one we already had
                oldValue, oldConfidence = filemd[key]
                if confidence > oldConfidence:
                    filemd[key] = (value, confidence)
            else:
                # this is new metadata, insert it with given confidence
                filemd[key] = (value, confidence)

        except KeyError:
            self.metadata[item] = {}
            # hack-o-matic
            self.metadata[item]['filename'] = (item, 1.0)
            self.metadata[item][key] = (value, confidence)

    def tagDirectory(self, directory):
        print 'tagging dir "' + directory + '"'
        self.files = self.getAllFilesInDir(directory)
        print 'files', self.files

        for filename in self.files:
            name = splitFilename(filename)            

            # user can first input some metadata for help if he so desires
            self.addMetadata(filename, 'serie', 'Futurama', 3.0)

            # apply list of heuristics on filenames to try to get as much metadata as possible
            # if would be nice if heuristics (only regexps?) could be translatable
            self.applyFilenameHeuristics(filename)

        print 'Found filename metadata', self.metadata

        # use the registered "web-plugins" that look on online database for metadata
        # can use previously discovered metadata either to refine a query or to
        # validate the results obtained
        self.applyOnlineHeuristics()

        # print the results
        #print self.metadata

    def applyOnlineHeuristics(self):
        self.web.singleSerieUrl(self.metadata[self.files[0]]['serie'][0])

    def fetchOnlineMetadata(self):
        # try to find each file in the db we just grabbed from the net
        for filename, md in self.metadata.items():
            # make this into a generic function passing [ 'season', 'epnumber' ] as argument
            print filename, md
            try:
                q = { 'season': str(int(md['season'][0])), 'epNumber': str(int(md['epNumber'][0])) }
            except KeyError:
                print 'WARNING: insufficient information for file:', filename
                continue

            result = [ episode for episode in self.web.episodes if isIncluded(q, episode) ]

            if len(result) == 1:
                print 'updating md for ', filename
                for key, value in result[0].items():
                    self.addMetadata(filename, key, value, 0.8)

        self.emit(SIGNAL('metadataUpdated'))

    def applyFilenameHeuristics(self, filename):
        name = splitFilename(filename)
        # heuristic 1: try to guess the season
        # this should contain also the confidence...
        rexps = [ 'season (?P<season>[0-9]+)',
                  '(?P<season>[0-9])x(?P<epNumber>[0-9][0-9])'
                  ]
        for n in name:
            result = matchAnyRegexp(n, rexps)
            if result:
                for key, value in result.items():
                    self.addMetadata(filename, key, value, confidence = 1.0)

        # heuristic 2: try to guess the serie title!
        if matchAnyRegexp(name[-2], ['season (?P<season>[0-9]+)$']):
            self.addMetadata(filename, 'serie', name[-3], 0.8)
        else:
            self.addMetadata(filename, 'serie', name[-2], 0.6)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    st = SeriesTagger()
    #st.getAllFilesInDir(sys.argv[1])
    st.tagDirectory(sys.argv[1])

    app.exec_()
        