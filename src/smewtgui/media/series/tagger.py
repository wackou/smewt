#!/usr/bin/python

import os
from os.path import join, split
import sys
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from serieobject import *
from mediatagger import MediaTagger
from collections import defaultdict
from itertools import groupby



# a metadata probability is a dict from name of property to a list of the possible
# candidates, which are pair of (value, confidence)
def newProbabilityFor(cls):
    mdprob = {}
    for key in cls.schema:
        mdprob[key] = []
    return mdprob



class SeriesTagger(MediaTagger):
    def __init__(self):
        super(SeriesTagger, self).__init__()

        # a dict from filename to metadata probabilities
        self.metadata = {}
        
        from webplugin_epguides import WebPluginEpGuides
        self.web = WebPluginEpGuides()
        self.connect(self.web, SIGNAL('done'),
                     self.fetchOnlineMetadata)


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


    # not redefined here, because the simple solver from the MediaTagger class
    # is enough for us, but you can and should subclass this method whenever
    # necessary
    def resolveProbabilities(self):
        return MediaTagger.resolveProbabilities(self.metadata)

    def tagDirectory(self, directory):
        print 'tagging dir "' + directory + '"'
        self.files = self.getAllFilesInDir(directory, [ '*.avi', '*.ogm', '*.mkv' ])
        #print 'files', self.files

        self.filenameMetadata = defaultdict(lambda: EpisodeObject())
        for filename in self.files:
            name = self.splitFilename(filename)            

            # user can first input some metadata for help if he so desires
            #self.filenameMetada[filename]['serie'] = 'Futurama'
            #self.filenameMetada[filename].confidence['serie'] = 3.0

            # apply list of heuristics on filenames to try to get as much metadata as possible
            # if would be nice if heuristics (only regexps?) could be translatable
            self.applyFilenameHeuristics(filename)

        # convert this metadata to a list of EpisodeObject
        self.metadata = []
        for filename, md in self.filenameMetadata.items():
            md['filename'] = filename
            md.confidence['filename'] = 1.0
            self.metadata.append(md)
        
        #print 'Found filename metadata', '\n'.join(map(str, self.metadata))
        

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
        #self.web.singleSerieUrl(self.metadata[self.files[0]]['serie'][0][0])
        # hack-o-matic
        sampleEpisode = self.filenameMetadata[self.filenameMetadata.keys()[0]]
        self.web.singleSerieUrl(sampleEpisode['serie'])

    def fetchOnlineMetadata(self):        
        # try to find each file we already have inside the db we just grabbed from the net
        for key in self.resolveProbabilities():
            #if any(key is None ) print 'BAD WARNING: insufficient information for file:', filename

            #print '---------'
            #print 'looking for', key
            for episode in self.web.episodes:
                if episode.getUniqueKey() == key:
                    #print 'Found MD:', episode
                    self.metadata.append(episode)

        self.emit(SIGNAL('metadataUpdated'))

    def applyFilenameHeuristics(self, filename):
        name = self.splitFilename(filename)
        md = self.filenameMetadata[filename]
        
        # heuristic 1: try to guess the season
        # this should contain also the confidence...
        rexps = [ 'season (?P<season>[0-9]+)',
                  '(?P<season>[0-9])x(?P<episodeNumber>[0-9][0-9])'
                  ]
        
        for n in name:
            for result in self.matchAllRegexp(n, rexps):
                for key, value in result.items():
                    #print 'Found MD:', filename, ':', key, '=', value
                    # automatic conversion, is that good?
                    value = md.schema[key](value)
                    md[key] = value
                    md.confidence[key] = 1.0

        # heuristic 2: try to guess the serie title!
        if self.matchAnyRegexp(name[1], ['season (?P<season>[0-9]+)$']):
            self.filenameMetadata[filename]['serie'] = name[2]
            self.filenameMetadata[filename].confidence['serie'] = 0.8
        else:
            self.filenameMetadata[filename]['serie'] = name[1]
            self.filenameMetadata[filename].confidence['serie'] = 0.6

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    st = SeriesTagger()
    #st.getAllFilesInDir(sys.argv[1])
    st.tagDirectory(sys.argv[1])

    app.exec_()
        
