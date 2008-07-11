#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
# Copyright (c) 2008 Ricard Marxer
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

from smewt.guessers.guesser import Guesser
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import copy
import sys
import re
from os.path import join, split

from media.series.serieobject import EpisodeObject

class EpisodeFilename(Guesser):
    def __init__(self):
        super(EpisodeFilename, self).__init__()
        
    def guess(self, mediaObject):
        if mediaObject.typename == 'Episode':
            if mediaObject['filename'] is not None:
                result = copy.copy(mediaObject)
                filename = result['filename']
                name = self.splitFilename(filename)
                
                # heuristic 1: try to guess the season
                # this should contain also the confidence...
                rexps = [ 'season (?P<season>[0-9]+)',
                          '(?P<season>[0-9])x(?P<episodeNumber>[0-9][0-9])'
                          ]
                
                # heuristic 2: try to guess the serie title!
                if self.matchAnyRegexp(name[1], ['season (?P<season>[0-9]+)$']):
                    result['serie'] = name[2]
                    result.confidence['serie'] = 0.8
                else:
                    result['serie'] = name[1]
                    result.confidence['serie'] = 0.6

                self.emit(SIGNAL('guessFinished'), [result])
            else:
                print 'Guesser: Does not contain ''filename'' metadata. Try when it has some info.'
        else:
            print 'Guesser: Not an EpisodeObject.  Cannot guess.'

        return super(EpisodeFilename, self).guess(mediaObject)

    def splitFilename(self, filename):
        root, path = split(filename)
        result = [ path ]
        # @todo this is a hack... How do we know we're at the root node?
        while len(root) > 1:
            root, path = split(root)
            result.append(path)
        return result
    
    def matchAnyRegexp(self, string, regexps):
        for regexp in regexps:
            result = re.compile(regexp, re.IGNORECASE).search(string)
            if result:
                return result.groupdict()
        return None



if __name__ == '__main__':
    app = QApplication(sys.argv)
    guesser = EpisodeFilename()
    mediaObject = EpisodeObject.fromDict({'filename': sys.argv[1]})
    
    def printResults(guesses):
        for guess in guesses:
            print guess.properties

    app.connect(guesser, SIGNAL('guessFinished'), printResults)
    
    guesser.guess(mediaObject)    
    
    app.exec_()
