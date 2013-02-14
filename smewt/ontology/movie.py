#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
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

from pygoo import BaseObject
from guessit.patterns import video_exts
from smewt.base import utils
from .media import Metadata


class Movie(Metadata):

    typename = 'Movie'

    schema = { 'title': unicode,
               'year': int,
               # more to come
               }

    valid = [ 'title' ]

    unique = [ 'title', 'year' ]

    order = [ 'title', 'year' ]

    converters = {}

    def niceString(self):
        return 'movie %s' % self.title

    @staticmethod
    def isValidMovie(filename):
        extPatterns = [ '*.' + ext for ext in video_exts ]
        return utils.matchFile(filename, extPatterns) #and getsize(filename) > 600 * 1024 * 1024



class Comment(BaseObject):
    schema = { 'metadata': Metadata,
               'author': unicode,
               'text': unicode,
               'date': int
               }

    reverse_lookup = { 'metadata': 'comments' }

    valid = [ 'metadata', 'author', 'date' ]
    unique = [ 'metadata', 'author', 'date' ]
