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

from PyQt4 import QtCore

class Guesser(QtCore.QObject):
    """Abstract class from which all guessers must inherit.  Guessers are objects that implement a slot called guess(self, mediaObject) that returns immediately, and begins the process of guessing metadata of the given mediaObject.
    When all guesses are made it emits a signal called guessFinished(guesses) which passes as argument a list of tuples containing the guessed MediaObjects and their associated confidence.
    
    """
    def __init__(self):
        super(Guesser, self).__init__()
    
    def guess(self, mediaObject):
        self.emit(QtCore.SIGNAL('guessFinished()'), [])
