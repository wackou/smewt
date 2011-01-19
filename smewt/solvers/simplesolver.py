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

from smewt.base import Media, Metadata
from smewt.solvers.solver import Solver
from smewt.base.textutils import levenshtein
import logging

log = logging.getLogger('smewt.solvers.simplesolver')


def exactMatch(baseGuess, md):
    return baseGuess.unique_key() == md.unique_key()

def fuzzyMatch(baseGuess, md):
    for p1, p2 in zip(baseGuess.unique_key(), md.unique_key()):
        if isinstance(p1, basestring):
            if p1 not in p2:
                return False
        else:
            if p1 != p2:
                return False
    return True

def fuzzyMatch2(baseGuess, md):
    for p1, p2 in zip(baseGuess.unique_key(), md.unique_key()):
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
    - first find the metadata which represents a unique object with
      highest confidence. If not found, the solver failed.
    - then merges all the information there is in all the guesses which have the
      same unique ID.
    '''

    def __init__(self, type):
        super(SimpleSolver, self).__init__()
        self.type = type

    def perform(self, query):
        self.checkValid(query)

        #query.display_graph()

        metadata = query.find_all(node_type = self.type)

        # 1- get a node that looks like it could be our potential candidate
        baseGuess, confidence = None, -1
        for md in metadata:
            if md.is_unique() and md.get('confidence') > confidence:
                baseGuess, confidence = md, md.get('confidence')

        if baseGuess is None:
            raise SmewtException('SimpleSolver could not find base guess')

        if confidence < 0.9:
            log.warning('Base guess for %s looks shady, confidence = %f: %s' % (query.find_one(Media).filename, confidence, baseGuess))
            #return self.found(query, None)

        # 2- once we have it, merge data from other nodes that look like him
        for md in metadata:
            # do not inadvertently overwrite some data we could have found from another instance
            if md is baseGuess:
                continue

            # if there is a match, merge the data
            if fuzzyMatch2(baseGuess, md):
                baseGuess.update(dict(md.items()))

        return self.found(query, baseGuess)
