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

from collections import defaultdict
from smewtdict import SmewtDict

class ValidatingSmewtDict(SmewtDict):
    def __init__(self, schema):
        super(ValidatingSmewtDict, self).__init__(schema)

    def __setitem__(self, key, value):
        if key in self.schema:
            # TODO: change this to an exception
            assert(value is None or type(value) == self.schema[key])

        defaultdict.__setitem__(self, key, value)
