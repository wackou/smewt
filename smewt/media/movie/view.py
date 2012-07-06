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

from pygoo import MemoryObjectGraph, ontology
from smewt.base import SmewtException, Media
from smewt.media import get_mako_template, render_mako_template
from movieobject import Movie
from smewt.base.utils import smewtDirectory, smewtMedia
ontology.import_class('Movie')


def render_mako(url, collection):
    tmap = { 'single': 'view_movie.mako',
             'all': 'view_all_movies.mako',
             'spreadsheet': 'view_movies_spreadsheet.mako',
             'unwatched': 'view_movies_spreadsheet.mako',
             'recent': 'view_recent_movies.mako'
             }

    t = get_mako_template('movie', tmap, url.viewType)

    if url.viewType == 'single':
        data = { 'movie': collection.find_one(Movie, title = url.args['title']) }

    elif url.viewType == 'all':
        data = { 'movies': collection.find_all(Movie) }

    elif url.viewType == 'spreadsheet':
        data = { 'title': 'ALL',
                 'movies': collection.find_all(Movie) }

    elif url.viewType == 'unwatched':
        data = { 'movies': [ m for m in collection.find_all(node_type = Movie)
                             if not m.get('watched') ],
                 'title': 'UNWATCHED' }

    elif url.viewType == 'recent':
        data = { 'movies': [ m for m in collection.find_all(node_type = Movie)
                             if m.get('lastViewed') is not None ],
                 'title': 'RECENT' }

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)

    data['url'] = url
    return t.render_unicode(**data)

def render(url, collection):
    return render_mako_template(render_mako, url, collection)
