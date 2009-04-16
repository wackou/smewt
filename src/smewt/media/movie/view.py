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

from Cheetah.Template import Template
from smewt.base import SmewtException, Graph, Media
from movieobject import Movie


def render(url, collection):
    '''This function always receive an URL and a full graph of all the collection as metadata input.
    This is the place to put some logic before the html rendering is done, such as filtering out
    items we don't want to display, or shape the data so that it's more suited for html rendering, etc...'''

    if url.viewType == 'single':
        # creates a new graph with all the media related to the given movie
        movieMD = collection.findAll(Movie, title = url.args['title'])[0]
        metadata = Graph()
        for f in collection.findAll(Media):
            if f.metadata == movieMD:
                metadata += f

        t = Template(file = 'smewt/media/movie/view_movie.tmpl',
                     searchList = { 'movie': metadata })

    elif url.viewType == 'all':
        t = Template(file = 'smewt/media/movie/view_all_movies.tmpl',
                     searchList = { 'movies': collection.findAll(Movie) })

    elif url.viewType == 'spreadsheet':
        t = Template(file = 'smewt/media/movie/view_movies_spreadsheet.tmpl',
                     searchList = { 'movies': collection.findAll(Movie) })

    elif url.viewType == 'unwatched':
        t = Template(file = 'smewt/media/movie/view_movies_spreadsheet.tmpl',
                     searchList = { 'movies': [ m for m in collection.findAll(Movie) if not m.watched ] })

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)

    return t.respond()




