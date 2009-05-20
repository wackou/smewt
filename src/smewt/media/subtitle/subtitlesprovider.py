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
'''

class SubtitleNotFoundError(SmewtException):
    pass



class MovieSubtitleProvider:
    '''This class represents the interface a plugin which downloads subtitles for movies
    should implement.'''

    def getAvailableSubtitles(movieName):
        '''This method should return a dict of language codes to a list of available
        subtitles for that language code.
        This can happen if there are multiple versions of the subtitles for the same movie.
        This can also happen if the movie spans multiple files.

        If no subtitle could be found, this method should return an empty dict.'''
        pass

    def getSubtitle(movieName, langCode, *args):
        '''This method should return the selected subtitle as a string.
        args should somehow indicate which subtitle we want if there are multiple choices available.
        If the subtitle could not be found, it should raise a SubtitleNotFoundError exception.

        TODO: what about the encoding? utf-8 sounds better, but IIRC mplayer prefers iso-8859-1...'''
        pass



class SeriesSubtitleProvider:
    '''This class represents the interface a plugin which downloads subtitles for series
    should implement.

    TODO: is it a good idea to allow asking/downloading for all the subtitles in a season at once?
    On the one hand, tvsubtitles groups them like that for complete seasons, so that would be a win
    on the bandwidth side.
    On the other hand, it might be a typical case of API over-engineering...'''

    def getAvailableSubtitles(seriesName, season, epNumber = None):
        '''This method should return a dict of language codes to a list of available
        subtitles for that language code.
        If epNumber is none, it should return the subtitles available for the whole season.

        If no subtitle could be found, this method should return an empty dict.'''
        pass

    def getSubtitle(seriesName, langCode, season, epNumber = None):
        '''This method should return the selected subtitle as a string.
        args should somehow indicate which subtitle we want if there are multiple choices available.
        If the subtitle could not be found, it should raise a SubtitleNotFoundError exception.

        TODO: what about the encoding? utf-8 sounds better, but IIRC mplayer prefers iso-8859-1...'''
        pass
