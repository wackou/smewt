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

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("smewt").addHandler(h)


from base import SmewtDict, ValidatingSmewtDict, SmewtException, SmewtUrl, SolvingChain, cachedmethod, EventServer, cache, utils, textutils
from base.mediaobject import Media, Metadata
log = logging.getLogger('smewt')


# used to be able to store settings for different versions of Smewt installed on the same computer, ie: a stable
# and a development version
ORG_NAME = 'DigitalGaia'
APP_NAME = 'Smewt-dev'

DEV_MODE = True



if DEV_MODE:
    log.info('Loading cache...')
    cache.load('/tmp/smewt.cache')

def shutdown():
    if DEV_MODE:
        log.info('Saving cache...')
        cache.save('/tmp/smewt.cache')


def setupLogging():
    """Sets up a nice colored logger as the main application logger (not only smewt itself)."""
    class ColoredFormatter(logging.Formatter):
        GREEN_FONT = "\x1B[0;32m"
        YELLOW_FONT = "\x1B[0;33m"
        BLUE_FONT = "\x1B[0;34m"
        RED_FONT = "\x1B[0;31m"
        RESET_FONT = "\x1B[0m"

        def __init__(self):
            self.fmt = '%(levelname)-8s ' + self.BLUE_FONT + '%(module)s:%(funcName)s' + self.RESET_FONT + ' -- %(message)s'
            logging.Formatter.__init__(self, self.fmt)

        def format(self, record):
            result = logging.Formatter.format(self, record)
            if record.levelno in (logging.DEBUG, logging.INFO):
                return self.GREEN_FONT + result
            elif record.levelno == logging.WARNING:
                return self.YELLOW_FONT + result
            else:
                return self.RED_FONT + result


    ch = logging.StreamHandler()
    ch.setFormatter(ColoredFormatter())
    logging.getLogger().addHandler(ch)


