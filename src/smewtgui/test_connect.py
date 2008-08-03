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

import dbus


def connect():
    no = dbus.SessionBus().get_object('com.smewt.Smewt', '/Smewtd')
    return dbus.Interface(no, 'com.smewt.Smewt.Smewtd')


def example():
    server = connect()

    # basic test
    print server.ping()

    # get movies
    #movies = server.queryMovies()
    #print 'Movies:', movies

    triples = server.query('', 'select ?P ?O ?Q where { $P $O $Q } limit 100')
    print triples

    '''
    # perform a lucene query
    query = 'baraka'
    print 'query lucene: ', query

    results = server.queryLucene(query)
    print 'results:'
    for name in results:
        print name


    # download a file
    friend = 'Wackou'
    filename = results[-1]
    print 'start downloading from', friend, ':', filename
    server.startDownload(friend, filename)
    '''

if __name__ == '__main__':
    example()
