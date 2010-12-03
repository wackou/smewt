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

from smewt.base import GraphAction, Metadata
from smewt.base.mediaobject import foundMetadata
import logging

log = logging.getLogger('smewt.solvers.solver')

class Solver(GraphAction):
    def __init__(self):
        super(Solver, self).__init__()

    def canHandle(self, query):
        try:
            query.find_one(Metadata)
        except:
            raise SmewtException('%s: not solving anything...' % self.__class__.__name__)

        log.debug('%s: trying to solve %s' % (self.__class__.__name__, query))

    def found(self, query, result):
        log.debug('%s: found for %s: %s' % (self.__class__.__name__, query, result))

        solved = foundMetadata(query, result)
        #solved.displayGraph()
        return solved