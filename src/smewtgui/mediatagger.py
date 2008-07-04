#!/usr/bin/python

import os
from os.path import join, split
import sys
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import fnmatch
from collections import defaultdict
from itertools import groupby


class MediaTagger(QObject):
    '''Base class for all media taggers.

    Doesn't have much of an interface, but contains a lot of utility functions.'

    derives from QObject, because it needs to send the Qt signal 'metadataUpdated'
    when it is done. (everything asynchronous!)
    '''

    @staticmethod
    def matchAnyRegexp(string, regexps):
        for regexp in regexps:
            result = re.compile(regexp, re.IGNORECASE).search(string)
            if result:
                return result.groupdict()
            return None

    @staticmethod
    def matchAllRegexp(string, regexps):
        result = []
        for regexp in regexps:
            match = re.compile(regexp, re.IGNORECASE).search(string)
            if match:
                result.append(match.groupdict())
        return result

    @staticmethod
    def isIncluded(d1, d2):
        for key, value in d1.items():
            try:
                if d2[key] != value:
                    return False
            except KeyError:
                return False
        return True


    @staticmethod
    def splitFilename(filename):
        root, path = split(filename)
        result = [ path ]
        # @todo this is a hack... How do we know we're at the root node?
        while len(root) > 1:
            root, path = split(root)
            result.append(path)
        return result


    @staticmethod
    def getAllFilesInDir(directory, filters = ['*']):
        allFiles = []
        #print 'get all files', directory[:-1]
        for root, dirs, files in os.walk(directory[:-1]):
            #print 'walking', root
            for filename in files:
                for filt in filters:
                    if fnmatch.fnmatch(filename, filt):
                        allFiles.append(join(root, filename))

        return allFiles


    @staticmethod
    def getAttributes(attrs, obj):
        result = [ obj[attr] for attr in attrs ]
        return tuple(result)

    @staticmethod
    def resolveProbabilities(metadata):
        '''A simple solver that just chooses as final metadata the one with the
        highest confidence, regardless of the others.

        This function takes as input a list of MediaObject, each of which
        representing an individual guess (either from the web, or the
        filename, ...)
        
        It returns a dictionary from unique keys to MediaObjects representing
        the metadata guessed for each object
        '''
        if not metadata:
            return {}

        #print '-'*100
        #print 'Resolving probs for', metadata
        #print '-'*100
        sample = metadata[0]

        result = defaultdict(lambda: sample.__class__())
        
        for key, mdprobs in groupby(metadata, key = lambda x: x.getUniqueKey()):
            #print 'resolving for', key
            for guess in mdprobs:
                #print 'guess:', guess
                for prop in guess.keys():
                    #print prop, 'before', result[key][prop], result[key].confidence[prop], 'now', guess[prop], guess.confidence[prop]
                    if guess.confidence[prop] > result[key].confidence[prop]:
                        result[key][prop] = guess[prop]
                        result[key].confidence[prop] = guess.confidence[prop]

        #print 'returning', result
                        
        return result

        
