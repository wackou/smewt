#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
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


class SimpleSolver(Solver):
    '''This solver implements this simple solving strategy:
    - first look if there's a metadata which represents a unique object with
      confidence > 0.9. If not found, the solver failed.
    - then merges all the information there is in all the guesses which have the
      same unique ID.
    '''

    def __init__(self):
        super(SimpleSolver, self).__init__()

    def start(self, query):
        self.checkValid(query)

        baseGuess = None
        for md in query.metadata:
            if md.isUnique() and md.confidence >= 0.9:
                baseGuess = copy.copy(md)

        if not baseGuess:
            self.found(query, None)
            return

        for md in query.metadata:
            if baseGuess.uniqueKey() == md.uniqueKey():
                baseGuess.merge(md)

        self.found(query, baseGuess)

