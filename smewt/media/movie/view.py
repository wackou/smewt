#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
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

from smewt.base import SmewtException
from smewt.media import lookup, render_mako_template
from movieobject import Movie


def render_mako(url, collection, smewtd):
    if url.viewType == 'single':
        tfilename = 'view_movie.mako'
        movie = collection.find_one(Movie, title = url.args['title'])
        data = { 'title': movie.title,
                 'movie': movie,
                 'smewtd': smewtd }

    elif not url.viewType:
        tfilename = 'view_all_movies.mako'
        data = { 'title': 'MOVIES',
                 'movies': collection.find_all(Movie) }

    elif url.viewType == 'spreadsheet':
        tfilename = 'view_movies_spreadsheet.mako'
        data = { 'title': 'MOVIE LIST',
                 'movies': collection.find_all(Movie) }

    elif url.viewType == 'unwatched':
        tfilename = 'view_movies_spreadsheet.mako'
        data = { 'movies': [ m for m in collection.find_all(node_type = Movie)
                             if not m.get('watched') and not m.get('lastViewed') ],
                 'title': 'UNWATCHED' }

    elif url.viewType == 'recent':
        tfilename = 'view_recent_movies.mako'
        data = { 'movies': [ m for m in collection.find_all(node_type = Movie)
                             if m.get('lastViewed') is not None ],
                 'title': 'RECENT' }

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)

    data['url'] = url
    t = lookup.get_template(tfilename)
    return t.render_unicode(**data)


def render(url, collection, smewtd):
    return render_mako_template(render_mako, url, collection, smewtd)
