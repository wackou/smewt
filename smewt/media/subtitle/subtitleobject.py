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

from smewt.base import Metadata


class Subtitle(Metadata):
    '''Metadata object used for representing subtitles.

    Note: the language property should be the 2-letter code as defined in:
    http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
    '''

    typename = 'Subtitle'

    schema = { 'metadata': Metadata,
               'language': unicode }

    valid = [ 'metadata' ]

    reverse_lookup = { 'metadata': 'subtitles' }

    order = [ 'metadata', 'language' ]

    unique = [ 'metadata', 'language' ]

    converters = {}
