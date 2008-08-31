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

from smewt.taggers.tagger import Tagger
from smewt.guessers import *
from smewt.solvers import *
from PyQt4.QtCore import SIGNAL

from smewt import Collection, SolvingChain
from smewt.media.series import Episode

class MagicEpisodeTagger(Tagger):
    def __init__(self):
        super(MagicEpisodeTagger, self).__init__()

        self.schain = SolvingChain(episodefilename.EpisodeFilename(),
                                   epguides.EpGuides(),
                                   naivesolver.NaiveSolver())

        # Connect the chain to our solved slot
        self.connect(self.schain, SIGNAL('finished'), self.solved)

    def solved(self, result):
        self.emit(SIGNAL('tagFinished'), result)

    def tag(self, media):
        if media.type() == 'video':
            if media.filename:
                query = Collection()
                query.media = [ media ]
                self.schain.start(query)
                return
            else:
                print 'Tagger: filename hasn\'t been set on Media object.'
        else:
            print 'Tagger: Not a video media.  Cannot tag.'

        # default tagger strategy if none other was applicable
        return super(MagicEpisodeTagger, self).tag(media)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    tagger = MagicEpisodeTagger()
    mediaObject = Episode.fromDict({'filename': sys.argv[1]})

    def printResults(tagged):
        print tagged

    app.connect(tagger, SIGNAL('tagFinished'), printResults)

    tagger.tag(mediaObject)

    app.exec_()
