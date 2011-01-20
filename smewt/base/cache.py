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

import cPickle
import logging

log = logging.getLogger('smewt.base.cache')

globalCache = {}

def clear():
    log.info('Cache: clearing memory cache')
    global globalCache
    globalCache = {}

def load(filename):
    log.info('Cache: loading cache from %s' % filename)
    global globalCache
    try:
        globalCache = cPickle.load(open(filename, 'rb'))
    except IOError:
        log.warning('Cache: Cache file doesn\'t exist')
    except EOFError:
        log.error('Cache: cache file is corrupted... Please remove it.')

def save(filename):
    log.info('Cache: saving cache to %s' % filename)
    cPickle.dump(globalCache, open(filename, 'wb'))


def cachedmethod(function):
    '''Makes a method use the cache. WARNING: this can NOT be used with static functions'''

    def cached(*args):
        # removed the first element of args for the key, which is the instance pointer
        # we don't want the cache to know which instance called it, it is shared among all
        # instances of the same class
        fkey = str(args[0].__class__), function.__name__
        key = (fkey, args[1:])
        if key in globalCache:
            return globalCache[key]

        result = function(*args)

        globalCache[key] = result

        return result

    cached.__doc__ = function.__doc__
    cached.__name__ = function.__name__

    return cached
