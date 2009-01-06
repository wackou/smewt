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

from smewt.solvers.solver import Solver
import copy
from smewt.base.mediaobject import Media, Metadata

class MergeSolver(Solver):

    def __init__(self, type):
        super(MergeSolver, self).__init__()
        self.type = type

    def start(self, query):
        self.checkValid(query)

        results = sorted(query.findAll(self.type), key = lambda x: -x.confidence)
        result = copy.copy(results[0])

        for md in results[1:]:
            for k, v in md.properties.items():
                # TODO: if the 2 values differ, merge only the one with the higher confidence
                result[k] = v

        self.found(query, result)
