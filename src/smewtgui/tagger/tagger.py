#!/usr/bin/python

import os
from os.path import join, split
import sys
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from serieobject import *

class MediaTagger:
    pass



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


# a metadata probability is a dict from name of property to a list of the possible
# candidates, which are pair of (value, confidence)
def newProbabilityFor(cls):
    mdprob = {}
    for key in cls.schema:
        mdprob[key] = []
    return mdprob



class SeriesTagger(QObject):
    def __init__(self):
        super(SeriesTagger, self).__init__()

        # a dict from filename to metadata probabilities
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
                if filename.endswith('.avi'):
                    allFiles.append(join(root, filename))

        
        return allFiles

    # this function just adds the probabilties for the properties, it is the job
    # of a solver to decide which one to keep in the end
    def addMetadata(self, item, key, value, confidence):
        try:
            filemd = self.metadata[item]
        except KeyError:
            self.metadata[item] = newProbabilityFor(EpisodeObject)
            # hack-o-matic
            self.metadata[item]['filename'] = [ (item, 1.0) ]

        self.metadata[item][key] = [ (MediaObject.parse(EpisodeObject, key, value), confidence) ]

    def resolveProbabilities(self):
        result = []
        print '-'*100
        print self.metadata
        print '-'*100
        #print 'Resolving probs for', self.metadata.values()
        for mdprobs in self.metadata.values():
            elem = EpisodeObject()
            for key, probs in mdprobs.items():
                if probs:
                    # simple strategy: keep the one with higher probability
                    # in case of a draw, keep the first one we already had
                    bestValue, maxProb = probs[0]
                    for value, prob in probs[1:]:
                        if prob > maxProb:
                            bestValue, maxProb = value, prob
                    elem[key] = bestValue
            result.append(elem)

        return result

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

        # now's the moment to decide: use a solver to resolve (possible) conflicts
        # in metadata and strip the confidence
        # note: at the moment, solver is called from outside

        # print the results
        #print self.metadata

    def applyOnlineHeuristics(self):
        self.web.singleSerieUrl(self.metadata[self.files[0]]['serie'][0][0])

    def fetchOnlineMetadata(self):
        # try to find each file in the db we just grabbed from the net
        for md in self.resolveProbabilities():
            # make this into a generic function passing [ 'season', 'epnumber' ] as argument
            filename = md['filename']
            print filename, md
            try:
                q = {}
                for key in EpisodeObject.unique:
                    q[key] = md[key]
            except KeyError:
                print 'BAD WARNING: insufficient information for file:', filename
                continue

            allEpisodes = [ EpisodeObject.fromDict(ep) for ep in self.web.episodes ]
            result = [ episode for episode in allEpisodes if isIncluded(q, episode) ]

            if len(result) == 0:
                print 'WARNING: insufficient information for file:', filename
                continue

            if len(result) == 1:
                print 'updating md for ', filename
                for key, value in result[0].properties.items():
                    self.addMetadata(filename, key, value, 0.8)

            if len(result) > 1:
                print 'ooh bad', result

        self.emit(SIGNAL('metadataUpdated'))

    def applyFilenameHeuristics(self, filename):
        name = splitFilename(filename)
        # heuristic 1: try to guess the season
        # this should contain also the confidence...
        rexps = [ 'season (?P<season>[0-9]+)',
                  '(?P<season>[0-9])x(?P<episodeNumber>[0-9][0-9])'
                  ]
        for n in name:
            result = matchAnyRegexp(n, rexps)
            if result:
                for key, value in result.items():
                    self.addMetadata(filename, key, value, confidence = 1.0)

        # heuristic 2: try to guess the serie title!
        if matchAnyRegexp(name[1], ['season (?P<season>[0-9]+)$']):
            self.addMetadata(filename, 'serie', name[2], 0.8)
        else:
            print '++++++++++++++++++++', filename
            print name
            self.addMetadata(filename, 'serie', name[1], 0.6)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    st = SeriesTagger()
    #st.getAllFilesInDir(sys.argv[1])
    st.tagDirectory(sys.argv[1])

    app.exec_()
        
