#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
# Copyright (c) 2008-2012 Nicolas Wack <wackou@smewt.com>
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

from pygoo import BaseObject, MemoryObjectGraph, Equal
from guessit.patterns import video_exts, subtitle_exts


# This file contains the 2 base MediaObject types used in Smewt:
#  - Media: is the type used to represent physical files on the hard disk.
#    It always has at least 2 properties: 'filename' and 'sha1'
#  - Metadata: is the type used to represent a media entity independent
#    of its physical location.
#


class Metadata(BaseObject):
    schema = { 'confidence': float,
               'watched': bool
               }

    valid = []

    def niceString(self):
        return str(self)


class Media(BaseObject):
    schema = { 'filename': unicode,
               'sha1': unicode,
               'metadata': Metadata,
               'watched': bool, # TODO: or is the one from Metadata sufficient?
               # TODO: needs to have datetime
               'lastAccessed': float, # seconds since the epoch

               # used by guessers and solvers
               'matches': Metadata
               }

    valid = [ 'filename' ]
    unique = [ 'filename' ]
    reverse_lookup = { 'metadata': 'files',
                       'matches': 'query' }

    types = { 'video': video_exts,
              'subtitle': subtitle_exts
              }


    def ext(self):
        return self.filename.split('.')[-1]

    # DEPRECATED: this has better alternatives, such as checking the class of
    #             an object, or using BaseObject.isinstance()
    def type(self):
        ext = self.ext().lower()
        for name, exts in Media.types.items():
            if ext in exts:
                return name
        return 'unknown type'

    def niceString(self):
        return str(self)


def foundMetadata(query, result, link = True):
    """Return a graph that contains:
     - the only Media object found in the query graph
     - the result object linked as metadata to the previous media object

    WARNING: this functions messes with the data in the query graph, do not reuse it after
    calling this function.
    """
    # TODO: check that result is valid
    solved = MemoryObjectGraph()

    # remove the stale 'matches' link before adding the media to the resulting graph
    #query.display_graph()
    media = query.find_one(Media)
    media.matches = []
    media.metadata = []
    m = solved.add_object(media)

    if result is None:
        return solved

    if isinstance(result, list):
        result = [ solved.add_object(n, recurse = Equal.OnLiterals) for n in result ]
    else:
        result = solved.add_object(result, recurse = Equal.OnLiterals)

    #solved.display_graph()
    if link:
        m.metadata = result

    return solved
