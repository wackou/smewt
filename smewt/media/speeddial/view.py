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
from smewt.base.utils import smewtDirectory

def render(url, collection):
    '''This function always receive an URL and a full graph of all the collection as metadata input.
    This is the place to put some logic before the html rendering is done, such as filtering out
    items we don't want to display, or shape the data so that it's more suited for html rendering, etc...'''
    t = Template(file = smewtDirectory('smewt', 'media', 'speeddial', 'speeddial.html'),
                 searchList = { 'info': None })

    return t.respond()




