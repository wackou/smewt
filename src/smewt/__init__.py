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

from base import SmewtDict, ValidatingSmewtDict, SmewtException, SmewtUrl, SolvingChain, cachedmethod, EventServer, utils, textutils
from base.mediaobject import Media, Metadata

import logging
logging.basicConfig(level = logging.INFO,
                    format = '%(levelname)-8s %(module)s:%(funcName)s -- %(message)s')

# we most likely never want this to be on debug mode, as it spits out way too much information
logging.getLogger('smewt.datamodel').setLevel(logging.INFO)
