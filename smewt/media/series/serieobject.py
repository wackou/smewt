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

class Series(Metadata):

    #typename = 'Series'

    schema = { 'title': unicode,
               'numberSeasons': int,
               #'episodeList': list
               }

    valid = [ 'title' ]
    unique = [ 'title' ]

    #converters = { 'episodeList': lambda x:x } #parseEpisodeList }


class Episode(Metadata):

    #typename = 'Episode'

    schema = { 'series': Series,
               'season': int,
               'episodeNumber': int,
               'title': unicode
               }

    valid = [ 'series', 'season', 'episodeNumber' ]
    reverse_lookup = { 'series': 'episodes' }
    #order = [ 'series', 'season', 'episodeNumber',  'title' ]

    unique = [ 'series', 'season', 'episodeNumber' ]

    converters = {}

