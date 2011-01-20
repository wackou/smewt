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
from pygoo import MemoryObjectGraph, ontology
from smewt.base import SmewtException, Media
from movieobject import Movie
from smewt.base.utils import smewtDirectory
ontology.import_class('Movie')

def render(url, collection):
    '''This function always receive an URL and a full graph of all the collection as metadata input.
    This is the place to put some logic before the html rendering is done, such as filtering out
    items we don't want to display, or shape the data so that it's more suited for html rendering, etc...'''

    # TODO: this is the place where we know which data we want to cache from the database to a MemoryObjectGraph

    if url.viewType == 'single':
        t = Template(file = smewtDirectory('smewt', 'media', 'movie', 'view_movie.tmpl'),
                     searchList = { 'movie': collection.find_one(Movie, title = url.args['title']) })

    elif url.viewType == 'all':
        t = Template(file = smewtDirectory('smewt', 'media', 'movie', 'view_all_movies.tmpl'),
                     searchList = { 'movies': collection.find_all(Movie) })

    elif url.viewType == 'spreadsheet':
        t = Template(file = smewtDirectory('smewt', 'media', 'movie', 'view_movies_spreadsheet.tmpl'),
                     searchList = { 'movies': collection.find_all(Movie),
                                    'title': 'ALL' })

    elif url.viewType == 'unwatched':
        t = Template(file = smewtDirectory('smewt', 'media', 'movie', 'view_movies_spreadsheet.tmpl'),
                     searchList = { 'movies': [ m for m in collection.find_all(node_type = Movie) if not m.get('watched') ],
                                    'title': 'UNWATCHED' })

    elif url.viewType == 'recent':
        t = Template(file = smewtDirectory('smewt', 'media', 'movie', 'view_recent_movies.tmpl'),
                     searchList = { 'movies': [ m for m in collection.find_all(node_type = Movie) if m.get('lastViewed') is not None ],
                                    'title': 'RECENT' })

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)

    result = t.respond()
    #open('/tmp/view.html', 'w').write(result.encode('utf-8'))
    return result
