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
import logging

class EpisodeTagger(Tagger):
    def __init__(self):
        super(EpisodeTagger, self).__init__()

        self.chain1 = SolvingChain(EpisodeFilename(), MergeSolver())
        self.chain2 = SolvingChain(EpisodeIMDB(), SimpleSolver())

        # Connect the chains to our slots
        self.connect(self.chain1, SIGNAL('finished'), self.gotFilenameMetadata)
        self.connect(self.chain2, SIGNAL('finished'), self.solved)

    def gotFilenameMetadata(self, result):
        self.filenameMetadata = result.metadata[0]
        self.chain2.start(result)

    def solved(self, result):
        logging.debug('Finished tagging: %s', result.media[0])
        if not result.metadata[0]:
            logging.warning('Could not find any tag for: %s' % result.media[0])
            # we didn't find any info outside of what the filename told us
            result.metadata = [ self.filenameMetadata ]
            result.links = [ (result.media[0], result.metadata[0]) ]

        self.emit(SIGNAL('tagFinished'), result)



    def tag(self, media):
        if media.type() in [ 'video', 'subtitle'] :
            if media.filename:
                query = Collection()
                query.media = [ media ]
                self.chain1.start(query)
                return
            else:
                print 'Tagger: filename hasn\'t been set on Media object.'
        else:
            print 'Tagger: Not a video media.  Cannot tag.'

        # default tagger strategy if none other was applicable
        return super(EpisodeTagger, self).tag(media)
