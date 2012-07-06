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

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions
from smewt.base.utils import smewtMedia

RELOAD_TEMPLATES = True
DEBUG_TEMPLATES = True

_tmpl_cache = {}

lookup = TemplateLookup(directories=[ smewtMedia('common'),
                                      smewtMedia('speeddial'),
                                      smewtMedia('movie'),
                                      smewtMedia('series')
                                      ],
                        strict_undefined=False,
                        filesystem_checks=RELOAD_TEMPLATES)

def get_mako_template(namespace, tmap, name):
    filename = tmap[name]
    return lookup.get_template(filename)


def render_mako_template(render_func, url, collection):
    try:
        result = render_func(url, collection)
        if DEBUG_TEMPLATES:
            open('/tmp/view.html', 'w').write(result.encode('utf-8'))
        return result
    except:
        return exceptions.html_error_template().render()


from series import *
from movie import *
from subtitle import *
