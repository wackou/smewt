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


# all the logic of rendering should be contained in the template
# we shall always pass only a list of the basic media object
# (eg for series, we have SerieObject, EpisodeObject, SeasonObject...
#  but the base type is EpisodeObject (a single file)
#  That means that if the view should represent a list of all
#  the series available, it needs to do its groupby by itself)
def render(name, episodes):
    #print '---- Rendering episode:', episodes

    if name == 'single':
        t = Template(file = 'media/series/view_episodes_by_season.tmpl',
                     searchList = { 'episodes': episodes })
    elif name == 'all':
        t = Template(file = 'media/series/view_all_series.tmpl',
                     searchList = { 'episodes': episodes })
    else:
        return 'Invalid view name'

    return t.respond()




