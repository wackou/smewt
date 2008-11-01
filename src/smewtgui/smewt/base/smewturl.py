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

from smewtexception import SmewtException

class SmewtUrl:
    def __init__(self, url):
        self.url = unicode(url)
        if not self.url.startswith('smewt://'):
            raise SmewtException('Could not create SmewtUrl from %s' % url)

        spath = self.url[8:].split('/')

        # rebind '/' that were escaped
        while '' in spath:
            idx = spath.index('')
            merged = spath[idx-1] + '/' + spath[idx+1]
            spath[idx-1:idx+1] = [ merged ]

        self.mediaType = spath[0]
        self.viewType = spath[1]

        try:
            self.args = spath[2:]
        except IndexError:
            self.args = None

    def __str__(self):
        return self.url.encode('utf-8')