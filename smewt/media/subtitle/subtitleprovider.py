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

'''
NOTES:

 - the API should be aware that there might be different releases for the same file (eg: multiple
   release groups). It should return as much info as possible so that we might try to match this
   info with the one we have from the movie itself

 - the API should be aware that some subtitles might span more than 1 file (eg: multiple CDs movies)

 - if the source of the subtitles allows downloading all of the subs for a season at once, this should
   be cached in the implementation, but should not appear in the API.

TODO: what about the encoding? utf-8 sounds better, but IIRC mplayer prefers iso-8859-1...
'''

from smewt.base import SmewtException

class SubtitleNotFoundError(SmewtException):
    pass



class SubtitleProvider:
    """This class represents the interface that needs to be implemented by a plugin which downloads
    subtitles for movies or series."""

    def canHandle(self, metadata):
        """This method returns whether this subtitle provider is able to handle the given object.

        Only objects which fulfill this condition should be handed to the getAvailableSubtitles
        method."""

        raise NotImplementedError


    def getAvailableSubtitles(self, metadata):
        """This method should return a graph of all available Subtitle metadata objects for
        the given Metadata (Movie, Episode, ...) object.

        If no subtitle could be found, this method should return an empty graph.

        It is assumed that the given Metadata object complies with the canHandle method.

        NB: This graph can contain multiple versions of the subtitle (different languages,
        different rips, ...) for the same object.
        The subtitles may also span multiple files (if the object (movie) is split in the same way)."""

        raise NotImplementedError


    def getSubtitle(self, subtitle):
        """This method should return the contents of the given subtitle as a string.
        The Subtitle object should be picked among the ones returned by the getAvailableSubtitles
        method.

        If the subtitle could not be found, a SubtitleNotFoundError exception should be raised."""

        raise NotImplementedError
