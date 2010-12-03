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

class GraphAction(object):
    """A GraphAction operates a transformation of a graph containing one Media object.
    In particular, they will tend to be either a Guesser, which will try to guess more
    information from the given media object (either from the filename, or from the web, ...),
    or a Solver, which will take the information in the graph and try to sum it up and only
    keep the relevant one."""

    def __init__(self):
        super(GraphAction, self).__init__()


    def canHandle(self, media):
        """Return silently if this GraphAction can handle the given media object.
        Should raise an exception otherwise."""
        raise NotImplementedError
        #if media[0].type() not in self.supportedTypes:
        #    raise SmewtException('Guesser: this guesser only supports files of type: %s but you provided a file of type: %s' % (str(self.supportedTypes), media[0].type()))


    def checkValid(self, query):
        """Check that our query graph contains only one MEdia object and that it can be handled
        by our GraphAction."""
        media = query.find_all(Media)
        if len(media) != 1:
            raise SmewtException('%s: your query should contain exactly 1 element in the query graph' % self.__class__.__name__)

        self.canHandle(query)


    def perform(self, query):
        """This method should do the actual work and return the result directly.
        When this method is called, ownership of the query graph is yielded to this GraphAction,
        which means that it can safely tamper with it."""
        raise NotImplementedError