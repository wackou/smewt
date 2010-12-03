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

from PyQt4.QtCore import SIGNAL, QObject
from smewt.base import SmewtException
from smewt.base.mediaobject import Media

class Guesser(QObject):
    """Abstract class from which all guessers must inherit.  Guessers are objects
    that implement a slot called start(self, query) that returns immediately, and
    begins the process of guessing metadata of the first element of the given
    Collection.media list.

    When all guesses are made it emits a signal called finished(guesses) which
    returns the original Collection augmented with the guesses it could have made.

    The following needs to be defined in derived classes:

    1- 'supportedTypes' which lists the media types for which this guesser can
        provide metadata.

    """

    def __init__(self):
        super(Guesser, self).__init__()

    def checkValid(self, query):
        '''Checks that we have only one object in Collection.media list and that
        its type is supported by our guesser'''
        media = query.find_all(node_type = Media)
        if len(media) != 1:
            raise SmewtException('Guesser: your query should contain exactly 1 element in the Collection.media list')

        if media[0].type() not in self.supportedTypes:
            raise SmewtException('Guesser: this guesser only supports files of type: %s but you provided a file of type: %s' % (str(self.supportedTypes), media[0].type()))


    def start(self, query):
        self.emit(SIGNAL('finished'), query)