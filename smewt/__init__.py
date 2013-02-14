#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
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

ORG_NAME = 'Falafelton'
APP_NAME = 'Smewt'

__version__ = '0.4-dev'

SMEWTD_INSTANCE = None


from appdirs import AppDirs
dirs = AppDirs(APP_NAME, ORG_NAME, version=__version__)

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("smewt").addHandler(h)



from guessit.slogging import setupLogging
import smewt.config

setupLogging(colored=True, with_time=True, with_thread=True)

logging.getLogger().setLevel(smewt.config.MAIN_LOGGING_LEVEL)
for name, level in smewt.config.LOGGING_LEVELS:
    logging.getLogger(name).setLevel(level)


from smewt.base import SmewtException, SolvingChain, cachedmethod, EventServer, cache, utils, textutils
from smewt.ontology import Media, Metadata
