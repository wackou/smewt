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
from smewt.datamodel import MemoryObjectGraph, Equal
from smewt.base import Media, Metadata
import logging

log = logging.getLogger('smewt.solvers.solver')

class Solver(QObject):
    """Abstract class from which all Solvers must inherit.  Solvers are objects
    that implement a slot called start(self, query) that returns immediately,
    and begins the process of solving the merge of mediaObjects.

    When a merge (the most probable mediaObject) has been found it emits a signal
    called finished(mediaObject) which passes as argument a mediaObject
    corresponding to the best solution or None in case no solution is available.
    """

    def __init__(self, type):
        super(Solver, self).__init__()
        self.type = type

    def checkValid(self, query):
        '''Checks that we have only one object in Collection.media list and that
        its type is supported by our guesser'''
        if len(query.findAll(type = Media)) != 1:
            raise SmewtException('Solver: your query should contain exactly 1 Media object')

        try:
            query.findOne(type = Metadata)
        except:
            raise SmewtException('Solver: not solving anything...')

        log.debug(self.__class__.__name__ + ' Solver: trying to solve %s', query)

    def found(self, query, result):
        query.displayGraph()
        # TODO: check that result is valid

        solved = MemoryObjectGraph()
        md = solved.addObject(result)

        # remove the stale 'matches' link before adding the media to the resulting graph
        media = query.findOne(type = Media)
        media.matches = []
        solved.addObject(media).metadata = md
        solved.displayGraph()

        log.debug('Solver: found for %s: %s', media, result)

        self.emit(SIGNAL('finished'), solved)

    def start(self, query):
        self.emit(SIGNAL('finished'), None)
