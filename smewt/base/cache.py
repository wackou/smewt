#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@smewt.com>
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

from __future__ import unicode_literals
from functools import wraps
import cPickle
import logging

log = logging.getLogger(__name__)

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


def cached_func_key(func, cls=None):
    return ('%s.%s' % (cls.__module__, cls.__name__) if cls else None, func.__name__)

def has_cached_func_value(func, args, kwargs={}):
    func_key = cached_func_key(func)
    key = (func_key, args, tuple(sorted(kwargs.items())))
    return key in globalCache

def log_cache(key, result=None):
    if result:
        res = unicode(result)
        if len(res) > 200:
            res = res[:100] + '   ...   ' + res[-100:]
        log.debug('Using cached value for %s(%s,%s), returns: %s' % (key + (res,)))
    else:
        log.debug('Computing value for %s(%s,%s)' % key)

def cachedfunc(function):
    """Make a function (not a class method) use the global cache."""

    @wraps(function)
    def cached(*args, **kwargs):
        func_key = cached_func_key(function)
        key = (func_key, args, tuple(sorted(kwargs.items())))
        if key in globalCache:
            result = globalCache[key]
            log_cache(key, result)
            return result

        log_cache(key)
        result = function(*args, **kwargs)
        globalCache[key] = result
        return result

    return cached


def cachedmethod(function):
    """Make a class method (not a module function) use the cache."""

    @wraps(function)
    def cached(*args, **kwargs):
        func_key = cached_func_key(function, args[0].__class__)
        # we need to remove the first element of args for the key, as it is the
        # instance pointer and we don't want the cache to know which instance
        # called it, it is shared among all instances of the same class
        key = (func_key, args[1:], tuple(sorted(kwargs.items())))
        if key in globalCache:
            result = globalCache[key]
            log_cache(key, result)
            return result

        log_cache(key)
        result = function(*args, **kwargs)
        globalCache[key] = result
        return result

    return cached
