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

from smewt.guessers.guesser import Guesser
from smewt import utils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import copy
import sys

from smewt.media.series import Episode

class EpisodeFilename(Guesser):

    supportedTypes = [ 'video' ]

    def __init__(self):
        super(EpisodeFilename, self).__init__()

    def guess(self, query):
        found = query.metadata
        mediaObject = query.media[0]

        if mediaObject.type() == 'video':
            #result = copy.copy(mediaObject)
            name = utils.splitFilename(mediaObject.filename)

            # heuristic 1: try to guess the season & epnumber using S01E02 and 1x02 patterns
            rexps = [ 'season (?P<season>[0-9]+)',
                      '(?P<season>[0-9]+)x(?P<episodeNumber>[0-9]+)',
                      'S(?P<season>[0-9]+)E(?P<episodeNumber>[0-9]+)'
                      ]

            for n in name:
                for match in utils.matchAllRegexp(n, rexps):
                    result = Episode()
                    result.confidence = 1.0
                    for key, value in match.items():
                        #print 'Found MD:', filename, ':', key, '=', value
                        result[key] = value
                    found += [ result ]


            # heuristic 2: try to guess the serie title from the parent directory!
            result = Episode()
            if utils.matchAnyRegexp(name[1], ['season (?P<season>[0-9]+)$']):
                result['serie'] = name[2]
                result.confidence = 0.8
            else:
                result['serie'] = name[1]
                result.confidence = 0.4
            found += [ result ]

        else:
            print 'Guesser: Not a video Media.  Cannot guess.'
            #resultMediaObjects.append(mediaObject)

        self.emit(SIGNAL('guessFinished'), query)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    guesser = EpisodeFilename()
    mediaObject = EpisodeObject.fromDict({'filename': sys.argv[1]})
    mediaObject.confidence['filename'] = 1.0
    mediaObjects = [mediaObject]

    def printResults(guesses):
        for guess in guesses:
            print guess

    app.connect(guesser, SIGNAL('guessFinished'), printResults)

    guesser.guess(mediaObjects)

    app.exec_()
