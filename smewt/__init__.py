#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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


__version__ = '0.2.1'

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("smewt").addHandler(h)


from base import SmewtException, SmewtUrl, SolvingChain, cachedmethod, EventServer, cache, utils, textutils
from base.mediaobject import Media, Metadata
log = logging.getLogger('smewt')


# used to be able to store settings for different versions of Smewt installed on the same computer, ie: a stable
# and a development version
ORG_NAME = 'Falafelton'
APP_NAME = 'Smewt'
SINGLE_APP_PORT = 8357
