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

from smewt.base import SmewtException, Config
from serieobject import Series, Episode
from smewt.media import get_mako_template, render_mako_template


def render_mako(url, collection):
    tmap = { 'single': 'view_episodes_by_season.mako',
             'all': 'view_all_series.mako',
             'suggestions': 'view_episode_suggestions.mako'
             }

    t = get_mako_template('series', tmap, url.viewType)

    if url.viewType == 'single':
        # FIXME: this definitely doesn't belong here...
        try:
            config = collection.find_one(Config)
        except ValueError:
            config = collection.Config(displaySynopsis = True)

        series = collection.find_one(Series, title=url.args['title'])
        data = { 'title': series.title,
                 'series': series,
                 'displaySynopsis': config.displaySynopsis }

    elif url.viewType == 'all':
        data = { 'title': 'SERIES',
                 'series': collection.find_all(Series) }

    elif url.viewType == 'suggestions':
        data = { 'title': 'SUGGESTIONS',
                 'episodes': [ ep for ep in collection.find_all(Episode) if 'lastViewed' in ep ] }

    else:
        raise SmewtException('Invalid view type: %s' % url.viewType)

    data['url'] = url
    return t.render_unicode(**data)


def render(url, collection):
    return render_mako_template(render_mako, url, collection)
