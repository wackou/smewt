#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2012, 2013 Nicolas Wack <wackou@smewt.com>
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

# Mininum severeness above which Smewt will report logging entries
MAIN_LOGGING_LEVEL = logging.INFO

# Individual levels for specific modules
LOGGING_LEVELS = [ ('smewt.base.cache', logging.INFO),
                   ('pygoo', logging.INFO)
                   ]

# Whether to use a cache that is saved/restored between sessions
PERSISTENT_CACHE = True

# Whether to use the http debug toolbar plugin for pyramid
PYRAMID_DEBUGTOOLBAR = False

# Whether to add file and line info to all print statements
DEBUG_PRINT = False

# Whether to reload mako templates from file every time or use the cache
# TODO: still used? should check with what pyramid does
RELOAD_MAKO_TEMPLATES = True

# Whether to regenerate the thumbnails for the speeddial at app startup
REGENERATE_THUMBNAILS = False
