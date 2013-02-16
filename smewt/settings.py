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

from smewt.base.utils import path
import smewt
import json
import atexit
import logging

log = logging.getLogger(__name__)

"""This module automatically loads (resp. saves) a single python dictionary
when it is loaded (resp. when the python interpreter exits).

This dictionary can contain anything, but it needs to be JSON-serializable.
"""

SETTINGS_FILENAME = path(smewt.dirs.user_data_dir, 'Smewt_preferences.json',
                         createdir=True)

settings = {}


def load():
    global settings
    try:
        settings = json.load(open(SETTINGS_FILENAME))
        log.debug('Successfully loaded settings from file: %s', SETTINGS_FILENAME)
    except:
        pass

def save():
    json.dump(settings, open(SETTINGS_FILENAME, 'w'))
    log.debug('Successfully saved settings to file: %s', SETTINGS_FILENAME)


def get(name, default=None):
    return settings.get(name, default)

def set(name, value):
    settings[name] = value


# automatically load from file when importing the module
load()

# save when python interpreter exits
atexit.register(save)
