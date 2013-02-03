#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2013 Nicolas Wack <wackou@smewt.com>
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

from pygoo import BaseObject
import json

class Feed(BaseObject):
    schema = { 'url': unicode,
               'title': unicode,
               # TODO: use datetime when pygoo permits it
               'lastUpdate': unicode,
               'lastTitle': unicode,
               'entries': unicode }

    valid = [ 'url', 'title' ]

    def toDict(self):
        return { 'url': self.url,
                 'title': self.title,
                 'lastUpdate': tuple(f for f in json.loads(self.lastUpdate)),
                 'lastTitle': self.lastTitle,
                 'entries': [ f for f in json.loads(self.get('entries', '[]')) ] }

    @staticmethod
    def fromDict(d, graph):
        return graph.Feed(url = d['url'],
                          title = d['title'],
                          lastUpdate = json.dumps(d['lastUpdate']),
                          lastTitle = d['lastTitle'],
                          entries = json.dumps(d['entries']))


class Config(BaseObject):
    """Config class for representing the application configuration as an in-database object."""
    schema = { 'displaySynopsis': bool,
               'feeds': Feed }
    valid = []
    reverse_lookup = { 'feeds': 'config' }
