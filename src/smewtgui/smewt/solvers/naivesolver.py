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

from smewt.solvers.solver import Solver
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import copy

from media.series.serieobject import EpisodeObject

class NaiveSolver(Solver):
    def __init__(self):
        super(NaiveSolver, self).__init__()
        
    def solve(self, mediaObjects):
        if not mediaObjects:
            return super(NaiveSolver, self).solve(mediaObject)
            
        resultMediaObject = copy.copy(mediaObjects[0])
        
        for mediaObject in mediaObjects[1:]:
            for k, v in mediaObject.properties.iteritems():
                if mediaObject.confidence.get(k, 0.0) > resultMediaObject.confidence.get(k, 0.0):
                    resultMediaObject[k] = v
                    
        self.emit(SIGNAL('solveFinished'), resultMediaObject)


if __name__ == '__main__':
    #TODO: write a test here
    pass
