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

from PyQt4 import QtCore

class Solver(QtCore.QObject):
    """Abstract class from which all Solvers must inherit.  Solvers are objects that implement a slot called solve(self, guesses) that returns immediately, and begins the process of solving the merge of mediaObjects.
    When a merge (the most probable mediaObject) has been found it emits a signal called solveFinished(mediaObject) which passes as argument a mediaObject corresponding to the best solution or None in case no solution is available.
    """
    def __init__(self):
        super(Solver, self).__init__()
    
    def solve(self, guesses):
        self.emit(QtCore.SIGNAL('solveFinished'), None)
