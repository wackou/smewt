#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008-2013 Nicolas Wack <wackou@smewt.com>
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

import datetime
import logging

log = logging.getLogger(__name__)

class Event:
    def __init__(self, text):
        self.timestamp = datetime.datetime.now()
        self.text = text

    def __str__(self):
        return '%s: %s' % (self.timestamp.ctime(), self.text)

    def __repr__(self):
        return str(self)


class EventList(object):
    def __init__(self):
        self.events = []

    def clear(self):
        self.events = []

    def add(self, event):
        self.events.append(event)


class EventServer:

    events = EventList()

    @staticmethod
    def publish(text):
        EventServer.events.add(Event(text))
        log.info(text)
