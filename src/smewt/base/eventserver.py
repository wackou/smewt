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

import datetime
from PyQt4.QtCore import Qt, QVariant, QAbstractListModel

class Event:
    def __init__(self, text):
        self.timestamp = datetime.datetime.now()
        self.text = text

    def __str__(self):
        return self.timestamp.ctime() + ': ' + self.text

class EventList(QAbstractListModel):
    def __init__(self):
        super(EventList, self).__init__()
        self.events = []

    def rowCount(self, parent):
        return len(self.events)

    def data(self, index, role = Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        return QVariant(str(self.events[index.row()]))

    def add(self, text):
        self.events.append(Event(text))
        # TODO: use dataChanged instead
        self.reset()


class EventServer:

    events = EventList()

    @staticmethod
    def publish(text):
        EventServer.events.add(text)
