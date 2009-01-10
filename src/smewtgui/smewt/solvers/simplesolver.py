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

from smewt import Media, Metadata
from smewt.solvers.solver import Solver
from smewt.utils import levenshtein
import copy
import logging


def exactMatch(baseGuess, md):
    return baseGuess.uniqueKey() == md.uniqueKey()

def fuzzyMatch(baseGuess, md):
    for p1, p2 in zip(baseGuess.uniqueKey(), md.uniqueKey()):
        if type(p1) == str or type(p1) == unicode:
            if p1 not in p2:
                return False
        else:
            if p1 != p2:
                return False
    return True

def fuzzyMatch2(baseGuess, md):
    for p1, p2 in zip(baseGuess.uniqueKey(), md.uniqueKey()):
        if type(p1) == str or type(p1) == unicode:
            # TODO: levenshtein doesn't cut it here, we need a better string distance
            if levenshtein(p1.lower(), p2.lower()) > 80:
                return False
        elif isinstance(p1, Metadata):
            if not fuzzyMatch2(p1, p2):
                return False
        else:
            if p1 != p2:
                return False
    return True


class SimpleSolver(Solver):
    '''This solver implements this simple solving strategy:
    - first look if there's a metadata which represents a unique object with
      confidence > 0.9. If not found, the solver failed.
    - then merges all the information there is in all the guesses which have the
      same unique ID.
    '''

    def __init__(self, type):
        super(SimpleSolver, self).__init__()
        self.type = type

    def start(self, query):
        self.checkValid(query)

        baseGuess = None
        metadata = query.findAll(self.type)

        for md in metadata:
            if md.isUnique() and md.confidence >= 0.9:
                baseGuess = copy.copy(md)
                break

        if not baseGuess:
            self.found(query, None)
            return

        for md in metadata:
            # do not inadvertently overwrite some data we could have found from another instance
            if md is baseGuess:
                continue

            # if there is a match, merge the data
            if fuzzyMatch2(baseGuess, md):
                baseGuess.merge(md)

        self.found(query, baseGuess)
