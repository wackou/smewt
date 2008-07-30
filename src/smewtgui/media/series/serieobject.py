#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
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


from mediaobject import MediaObject

def parseEpisodeList(string):
    # blah
    return []


class SerieObject(MediaObject):

    typename = 'Serie'

    schema = { 'title': unicode,
               'numberSeasons': int,
               'episodeList': list
               }

    unique = [ 'title' ]

    converters = { 'episodeList': parseEpisodeList }



    def __init__(self):
        MediaObject.__init__(self)

    @staticmethod
    def fromDict(d):
        result = SerieObject()
        MediaObject.readFromDict(result, headers, row)
        return result

    @staticmethod
    def fromRow(headers, row):
        result = SerieObject()
        MediaObject.readFromRow(result, headers, row)
        return result


class EpisodeObject(MediaObject):

    typename = 'Episode'

    schema = { 'serie': unicode,
               'season': int,
               'episodeNumber': int,
               'title': unicode
               }

    unique = [ 'serie', 'season', 'episodeNumber' ]

    converters = {}

    def __init__(self):
        MediaObject.__init__(self)

    @staticmethod
    def fromDict(d):
        result = EpisodeObject()
        MediaObject.readFromDict(result, d)
        return result

    @staticmethod
    def fromRow(headers, row):
        result = EpisodeObject()
        MediaObject.readFromRow(result, headers, row)
        return result
