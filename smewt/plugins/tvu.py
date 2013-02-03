#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2012 Nicolas Wack <wackou@smewt.com>
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

from bs4 import BeautifulSoup
from guessit.textutils import clean_string
from smewt.base.cache import cachedfunc, has_cached_func_value
import requests
import json
import os.path
import logging

log = logging.getLogger(__name__)


def clean_feedtitle(title):
    return title.replace('[ed2k]', '').replace('tvunderground.org.ru:', '')

def clean_eptitle(title):
    if not title:
        return 'None'
    return os.path.splitext(' - '.join(title.replace('[ed2k] ', '').split(' - ')[1:]))[0]


@cachedfunc
def get_showlist_for_letter(l):
    log.info('Looking for shows starting with letter: %s' % l)
    url = 'http://tvu.org.ru/index.php?show=show&bst=%s' % l
    r = requests.get(url)
    # force utf-8 coding, as it seems it doesn't detect it correctly
    r.encoding = 'utf-8'
    bs = BeautifulSoup(r.text)
    tvshows = bs.find(id='main').find('table').find_all('tr')

    shows = []
    for show in tvshows:
        show = show('td')[1]
        showname = show.text.strip()
        showurl = show.find('a')['href']
        showid = showurl.split('=')[-1]
        shows.append((showname, showid))

    return shows

def get_show_mapping(only_cached=False):
    # FIXME: use a session to share the connections between all the requests
    shows = []
    for l in [ 'num' ] + list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
        if only_cached:
            if has_cached_func_value(get_showlist_for_letter, (l,)):
                shows.extend(get_showlist_for_letter(l))
        else:
            shows.extend(get_showlist_for_letter(l))

    #print 'Found %d TV shows' % len(shows)
    return shows

@cachedfunc
def get_seasons_for_showid(sid, title=None):
    url = 'http://tvu.org.ru/index.php?show=season&sid=%s' % sid
    r = requests.get(url)
    r.encoding = 'utf-8'

    feeds = []
    open('/tmp/tvub.html', 'w').write(r.text.encode('utf-8'))
    bs = BeautifulSoup(r.text)
    dubbed = bs.find(id='main').find_all('table')
    for d in dubbed:
        rows = d('tr')
        dub_lang = rows[0].find('img')['alt']
        result = []
        for season in d('tr')[2:]:
            cells = season('td')
            source, season, format = cells[0].text, int(cells[1].text), cells[2].text

            stitle = cells[3].find('a').text.strip()
            # remove series name if it appears in front
            if title and stitle.lower().startswith(title.lower()):
                stitle = clean_string(stitle[len(title):])
            link = 'http://tvu.org.ru/' + cells[3].find('a')['href']
            feedid = link.split('=')[-1]
            feedlink = 'http://tvu.org.ru/rss.php?se_id=%s' % feedid
            status = cells[3].find('i').text

            sub_lang = None
            subflag_td = cells[4].find('img')
            if subflag_td:
                sub_lang = subflag_td['alt']

            year = int(cells[5].text)

            result.append((source, season, format, stitle,
                           status, sub_lang, year, feedlink))

        feeds.append((dub_lang, result))

    return feeds

if __name__ == '__main__':
    if os.path.exists('/tmp/shows.json'):
        shows = json.loads(open('/tmp/shows.json').read())
    else:
        shows = get_show_mapping()
        open('/tmp/shows.json', 'w').write(json.dumps(shows))


    shows = dict(shows)

    sid = shows['Mentalist, The']

    feeds = get_seasons_for_showid(sid)

    for lang, lfeeds in feeds:
        print '-'*100
        print 'Dubbed in', lang
        print '-'*100
        for feed in lfeeds:
            print '%s - %s - %s || %s (%s) || %s - %s || %s' % feed
