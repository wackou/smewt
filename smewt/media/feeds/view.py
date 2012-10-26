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
import logging

log = logging.getLogger(__name__)

def render_mako(url, collection, smewtd):
    t = lookup.get_template('feeds.mako')

    return t.render_unicode(title='FEEDS',
                            url=url, feedWatcher=smewtd.feedWatcher)

def render(url, collection, smewtd):
    return render_mako_template(render_mako, url, collection, smewtd)
