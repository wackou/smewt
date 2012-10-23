#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2012 Nicolas Wack <wackou@smewt.com>
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

from smewt.media import lookup, render_mako_template
from smewt.base import utils
from smewt.plugins import tvudatasource
from guessit.textutils import reorder_title
import json
import os.path
import logging

log = logging.getLogger(__name__)

def render_mako(url, collection):
    t = lookup.get_template('tvu.mako')

    tvuShowsCacheFile = os.path.join(utils.smewtUserDirectory('tvu'), 'showsid.cache')
    try:
        shows = json.loads(open(tvuShowsCacheFile).read())
    except IOError:
        shows = dict(tvudatasource.get_show_mapping())
        open(tvuShowsCacheFile, 'w').write(json.dumps(shows))


    try:
        sid = shows[url.args['series']]
        feeds = tvudatasource.get_seasons_for_showid(sid, title=reorder_title(url.args['series']))
    except KeyError:
        feeds = []

    return t.render_unicode(title='TVU.ORG.RU',
                            url=url, shows=shows.keys(), feeds=feeds)

def render(url, collection):
    return render_mako_template(render_mako, url, collection)
