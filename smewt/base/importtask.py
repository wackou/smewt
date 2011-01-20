#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from pygoo import MemoryObjectGraph, Equal
from smewt.base import Media, Task
import logging

log = logging.getLogger('smewt.importtask')

class ImportTask(Task):
    def __init__(self, collection, taggerType, filename):
        super(ImportTask, self).__init__()
        self.collection = collection
        self.taggerType = taggerType
        self.filename = filename

    def perform(self):
        query = MemoryObjectGraph()
        query.Media(filename = self.filename)
        result = self.taggerType().perform(query)

        # TODO: check that we actually found something useful
        #result.display_graph()

        # import the data into our collection
        self.collection.add_object(result.find_one(Media),
                                   recurse = Equal.OnUnique)

