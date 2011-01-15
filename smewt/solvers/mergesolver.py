#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
# Copyright (c) 2011 Nicolas Wack <wackou@gmail.com>
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

from smewt.base import GraphAction, Media, Metadata
from smewt.solvers.solver import Solver


class MergeSolver(Solver):
    """A MergeSolver finds all nodes of the given type in a graph and merges their data into a single one.

    Each node should have a 'confidence' attribute that will be used for resolving conflicts. Only the value
    with the highest confidence is kept in the end."""

    def __init__(self, type):
        super(MergeSolver, self).__init__()
        self.type = type

    def perform(self, query):
        self.checkValid(query)

        results = sorted(query.find_all(node_type = self.type), key = lambda x: -x.confidence)

        # we have ownership over the query graph, so we can modify its elements
        result = results[0]
        for md in results[1:]:
            for k, v in md.explicit_items():
                if k == 'confidence' or k in result.keys():
                    continue
                result.set(k, v)

        return self.found(query, result)
