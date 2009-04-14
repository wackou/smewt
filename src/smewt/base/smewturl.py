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
from urlparse import ParseResult, urlparse, urlunparse
from urllib import urlencode, unquote_plus
import textutils

class SmewtUrl:
    def __init__(self, type=None, path=None, args = {}, url = None):
        if type and path and not url:
            if path[0] != '/': path = '/' + path
            args = textutils.toUtf8(args)
            self.spath = ParseResult('http', type, path, '', urlencode(args), None)

        elif url and not type and not path:

            if not unicode(url).startswith('smewt://'):
                raise SmewtException('Could not create SmewtUrl from %s' % url)

            url = str(url).replace('smewt://', 'http://')
            self.spath = urlparse(url)
        else:
            raise SmewtException('SmewtUrl: you need to specify either a string url or the components of the SmewtUrl you want to build')

        # set member vars in function of url type
        self.mediaType = self.viewType = self.actionType = None

        try:
            if self.spath.netloc == 'media':
                self.mediaType, self.viewType = self.spath.path.split('/')[1:]
            elif self.spath.netloc == 'action':
                self.actionType, = self.spath.path.split('/')[1:]
            elif self.spath.netloc == 'feedwatcher':
                pass
            else:
                raise SmewtException("SmewtUrl: invalid url type '%s'" % self.spath.netloc)

        except ValueError:
            raise SmewtException("SmewtUrl: incomplete url '%s'" % self)

        # TODO: in python 2.6 use parse_qs
        if self.spath.query:
            self.args = dict([ kv.split('=') for kv in self.spath.query.split('&') ])
            for key, value in self.args.items():
                self.args[unquote_plus(key)] = unquote_plus(value).decode('utf-8')

    def __str__(self):
        return urlunparse(self.spath).replace('http://', 'smewt://')

    def __unicode__(self):
        return urlunparse(self.spath).replace('http://', 'smewt://')
