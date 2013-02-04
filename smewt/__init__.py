#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
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


__version__ = '0.4-dev'

import logging

MAIN_LOGGING_LEVEL = logging.INFO
LOGGING_LEVELS = [ ('smewt.base.cache', logging.INFO)
                   ]

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("smewt").addHandler(h)

from guessit.slogging import setupLogging
setupLogging(colored=True, with_time=True, with_thread=True)

logging.getLogger().setLevel(MAIN_LOGGING_LEVEL)
for name, level in LOGGING_LEVELS:
    logging.getLogger(name).setLevel(level)

# add our 3rd party libraries (git modules) path in front of the python path,
# so that those modules get imported with preference to the system ones
# FIXME: somehow this doesn't play well with pyramid...
import sys, os.path
spath = os.path.join(os.path.split(__file__)[0], '3rdparty')
sys.path = [ spath ] + sys.path

from base import SmewtException, SmewtUrl, SolvingChain, cachedmethod, EventServer, cache, utils, textutils
from base.mediaobject import Media, Metadata
from PyQt4.QtCore import QCoreApplication

log = logging.getLogger('smewt')


# used to be able to store settings for different versions of Smewt installed on the same computer, ie: a stable
# and a development version
ORG_NAME = 'Falafelton'
APP_NAME = 'Smewt-dev'
SINGLE_APP_PORT = 8358

SMEWTD_INSTANCE = None

import atexit
from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    QCoreApplication.setOrganizationName(ORG_NAME)
    QCoreApplication.setOrganizationDomain('smewt.com')
    QCoreApplication.setApplicationName(APP_NAME)

    global SMEWTD_INSTANCE
    from smewt.base import SmewtDaemon
    SMEWTD_INSTANCE = SmewtDaemon()

    atexit.register(SmewtDaemon.quit, SMEWTD_INSTANCE)

    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('user', utils.smewtUserPath(), cache_max_age=3600)

    config.add_route('home', '/')
    config.add_route('speeddial', '/speeddial')
    config.add_route('media', '/media')
    config.add_route('feeds', '/feeds')
    config.add_route('tvu', '/tvu')

    config.add_route('movies_table', '/movies/table')
    config.add_route('recent_movies', '/movies/recent')
    config.add_route('unwatched_movies', '/movies/unwatched')
    config.add_route('all_movies', '/movies')
    config.add_route('movie', '/movie/{title}')
    config.add_route('no_movie', '/movie')

    config.add_route('all_series', '/series')
    config.add_route('series_suggestions', '/series/suggestions')
    config.add_route('series', '/series/{title}')

    config.add_route('config_get', '/config/get/{name}')
    config.add_route('config_set', '/config/set/{name}')

    config.add_route('action', '/action/{action}')
    config.add_route('info', '/info/{name}')

    config.add_route('preferences', '/preferences')
    config.add_route('controlpanel', '/controlpanel')


    config.scan()
    return config.make_wsgi_app()