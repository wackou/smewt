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


import atexit
import smewt
import smewt.config
from pyramid.config import Configurator


def main():
    """ This function returns a Pyramid WSGI application."""
    settings = { 'pyramid.reload_templates': smewt.config.RELOAD_MAKO_TEMPLATES,
                 'pyramid.debug_authorization':  False,
                 'pyramid.debug_notfound': False,
                 'pyramid.debug_routematch':  False,
                 'pyramid.default_locale_name': 'en',
                 'pyramid.includes': 'pyramid_debugtoolbar' if smewt.config.PYRAMID_DEBUGTOOLBAR else ''
                 }

    from smewt.base import SmewtDaemon
    smewt.SMEWTD_INSTANCE = SmewtDaemon()

    atexit.register(SmewtDaemon.quit, smewt.SMEWTD_INSTANCE)

    config = Configurator(settings=settings)
    config.add_static_view('static', 'smewt:static', cache_max_age=3600)
    config.add_static_view('user', smewt.dirs.user_data_dir, cache_max_age=3600)

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


    config.scan('smewt')
    app = config.make_wsgi_app()


    from waitress import serve
    serve(app, host='0.0.0.0', port=6543)


if __name__ == '__main__':
    main()


""" TODO: profiling
    if len(sys.argv) > 1 and sys.argv[1] == '--profile':
        try:
            import yappi

        except ImportError:
            print 'You need to install the yappi python module to profile Smewt!'
            sys.exit(1)

        try:
            yappi.start(True)
            main()

        finally:
            yappi.stop()

            print '\n\nSORTED BY SUB TIME'
            yappi.print_func_stats(sort_type=yappi.SORTTYPE_TSUB,
                                   limit=20)
            print '\n\nSORTED BY TOTAL TIME'
            yappi.print_func_stats(sort_type=yappi.SORTTYPE_TTOT,
                                   limit=20)
            print '\n\nTHREAD STATS'
            yappi.print_thread_stats()

            filename = 'callgrind.out.%d' % os.getpid()
            with open(filename, 'w') as f:
                yappi.write_callgrind_stats(f)
            print '\nWrote callgrind output to %s' % filename
"""