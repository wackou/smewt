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

from mako.template import Template
from mako import exceptions
from pygoo import MemoryObjectGraph, ontology
from smewt.base import SmewtException, Media
from movieobject import Movie
from smewt.base.utils import smewtDirectory, smewtMedia
ontology.import_class('Movie')

RELOAD_TEMPLATES = True
DEBUG_TEMPLATES = True

_tmpl_cache = {}

def get_mako_template(name):
    tmap = { 'single': 'view_movie.mako',
             'all': 'view_all_movies.mako',
             'spreadsheet': 'view_movies_spreadsheet.mako',
             'unwatched': 'view_movies_spreadsheet.mako',
             'recent': 'view_recent_movies.mako'
             }

    filename = tmap[name]
    if RELOAD_TEMPLATES:
        t = Template(filename=smewtMedia('movie', filename))
        _tmpl_cache[name] = t
        return t
    else:
        if name in _tmpl_cache:
            return _tmpl_cache[name]
        else:
            t = Template(filename=smewtMedia('movie', filename),
                         strict_undefined=True)
            _tmpl_cache[name] = t
            return t

def render_mako(url, collection):
    t = get_mako_template(url.viewType)

    if url.viewType == 'single':
        return t.render_unicode(movie=collection.find_one(Movie, title = url.args['title']))

    elif url.viewType == 'all':
        return t.render(movies=collection.find_all(Movie))

    elif url.viewType == 'spreadsheet':
        return t.render(title='ALL', movies=collection.find_all(Movie))

    elif url.viewType == 'unwatched':
        return t.render(movies=[ m for m in collection.find_all(node_type = Movie)
                                 if not m.get('watched') ],
                        title='UNWATCHED')

    elif url.viewType == 'recent':
        return t.render(movies=[ m for m in collection.find_all(node_type = Movie)
                                 if m.get('lastViewed') is not None ],
                        title='RECENT')

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)


def render(url, collection):
    '''This function always receive an URL and a full graph of all the collection as metadata input.
    This is the place to put some logic before the html rendering is done, such as filtering out
    items we don't want to display, or shape the data so that it's more suited for html rendering, etc...'''

    try:
        result = render_mako(url, collection)
        if DEBUG_TEMPLATES:
            open('/tmp/view.html', 'w').write(result.encode('utf-8'))
        return result
    except:
        return exceptions.html_error_template().render()
