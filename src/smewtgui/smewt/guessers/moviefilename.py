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

from smewt.guessers.guesser import Guesser
from smewt import utils, textutils
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import re
import logging

log = logging.getLogger('smewt.guessers.moviefilename')

from smewt import Media, Metadata
from smewt.media import Movie

def validYear(year):
    try:
        return int(year) > 1920 and int(year) < 2015
    except ValueError:
        return False

def guessXCT(filename):
    if not '[XCT]' in filename:
        return filename, {}

    filename = filename.replace('[XCT]', '')
    md = {}

    try:
        # find metadata
        mdstr = textutils.matchRegexp(filename, '\[(?P<mdstr>.*?)\]')['mdstr']
        filename = filename.replace(mdstr, '')

        # find subs
        subs = textutils.matchRegexp(mdstr, 'St[{\(](?P<subs>.*?)[}\)]')['subs']
        mdstr.replace(subs, '')
        md['subs'] = subs.split('-')

        # find audio
        audio = textutils.matchRegexp(mdstr, 'aac[0-9\.-]*[{\(](?P<audio>.*?)[}\)]')['audio']
        mdstr.replace(audio, '')
        md['language'] = audio.split('-')

        # find year: if we found it, then the english title of the movie is either what's inside
        # the parentheses before the year, or everything before the year
        title = filename
        years = [ m['year'] for m in textutils.multipleMatchRegexp(filename, '(?P<year>[0-9]{4})') if validYear(m['year']) ]
        if len(years) == 1:
            title = filename[:filename.index(years[0])]
        elif len(years) >= 2:
            log.warning('Ambiguous filename: possible years are ' + ', '.join(years))

        try:
            title = textutils.matchRegexp(title, '\((?P<title>.*?)\)')['title']
        except:
            pass

        md['title'] = title

    finally:
        return title, md

def cleanMovieFilename(filename):
    import os.path
    filename = os.path.basename(filename)
    md = {}

    # TODO: fix those cases

    # first apply specific methods which are very strict but have a very high confidence
    filename, md = guessXCT(filename)

    # DVDRip.Xvid-$(grpname)
    grpnames = [ '\.Xvid-(?P<releaseGroup>.*?)\.',
                 '\.DivX-(?P<releaseGroup>.*?)\.'
                 ]
    editions = [ '(?P<edition>(special|unrated|criterion).edition)'
                 ]
    audio = [ '(?P<audioChannels>5\.1)' ]

    specific = grpnames + editions + audio
    for match in textutils.matchAllRegexp(filename, specific):
        for key, value in match.items():
            md[key] = value
            filename = filename.replace(value, '')


    # remove punctuation for looser matching now
    seps = [ ' ', '-', '.', '_' ]
    for sep in seps:
        filename = filename.replace(sep, ' ')

    # TODO: replace this with a getMetadataGroups function that splits on parentheses/braces/brackets
    remove = [ '[', ']', '(', ')' ]
    for rem in remove:
        filename = filename.replace(rem, '')

    name = filename.split(' ')


    properties = { 'format': [ 'DVDRip', 'HDDVD', 'HDDVDRip', 'BDRip', 'R5', 'HDRip', 'DVD', 'Rip' ],
                   'container': [ 'avi', 'mkv', 'ogv', 'wmv', 'mp4', 'mov' ],
                   'screenSize': [ '720p' ],
                   'videoCodec': [ 'XviD', 'DivX', 'x264' ],
                   'audioCodec': [ 'AC3', 'DTS', 'AAC' ],
                   'language': [ 'english', 'eng',
                                 'spanish', 'esp',
                                 'italian',
                                 'vo', 'vf'
                                 ],
                   'releaseGroup': [ 'ESiR', 'WAF', 'SEPTiC', '[XCT]', 'iNT', 'PUKKA', 'CHD', 'ViTE', 'DiAMOND', 'TLF',
                                     'DEiTY', 'FLAiTE', 'MDX', 'GM4F', 'DVL', 'SVD', 'iLUMiNADOS', ' FiNaLe', 'UnSeeN' ],
                   'other': [ '5ch', 'PROPER', 'REPACK', 'LIMITED', 'DualAudio', 'iNTERNAL', 'Audiofixed',
                              'classic', # not so sure about this one, could appear in a title
                              'ws', # widescreen
                              ],
                   }

    # ensure they're all lowercase
    for prop, value in properties.items():
        properties[prop] = [ s.lower() for s in value ]

    # get specific properties
    for prop, value in properties.items():
        for part in list(name):
            if part.lower() in value:
                md[prop] = part
                name.remove(part)

    # get year
    def validYear(year):
        try:
            return int(year) > 1920 and int(year) < 2015
        except ValueError:
            return False


    for part in list(name):
        year = textutils.stripBrackets(part)
        if validYear(year):
            md['year'] = int(year)
            name.remove(part)

    # remove ripper name
    for by, who in zip(name[:-1], name[1:]):
        if by.lower() == 'by':
            name.remove(by)
            name.remove(who)
            md['ripper'] = who

    # subtitles
    for sub, lang in zip(name[:-1], name[1:]):
        if sub.lower() == 'sub':
            name.remove(sub)
            name.remove(lang)
            md['subtitleLanguage'] = lang

    # get CD number (if any)
    cdrexp = re.compile('[Cc][Dd]([0-9]+)')
    for part in list(name):
        try:
            md['cdNumber'] = int(cdrexp.search(part).groups()[0])
            name.remove(part)
        except AttributeError:
            pass

    name = ' '.join(name)

    # last chance on the full name: try some popular regexps
    general = [ '(?P<dircut>director\'s cut)',
                '(?P<edition>edition collector)' ]
    websites = [ 'sharethefiles.com' ]
    websites = [ '(?P<website>%s)' % w.replace('.', ' ') for w in websites ] # dots have been previously converted to spaces
    rexps = general + websites

    matched = textutils.matchAllRegexp(name, rexps)
    for match in matched:
        for key, value in match.items():
            name = name.replace(value, '')

    # try website names
    # TODO: generic website url guesser
    websites = [ 'sharethefiles.com' ]



    # remove leftover tokens
    name = name.replace('()', '')
    name = name.replace('[]', '')


    md['title'] = name
    return md


class MovieFilename(Guesser):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(MovieFilename, self).__init__()

    def start(self, query):
        self.checkValid(query)

        media = query.findAll(Media)[0]

        movie = cleanMovieFilename(media.filename)

        query += Movie(dictionary = movie)

        # heuristic 1: try to guess the season & epnumber using S01E02 and 1x02 patterns
        #query += result

        # cleanup a bit by removing unlikely eps numbers which are probably numbers in the title
        # or even dates in the filename, etc...

        # heuristic 2: try to guess the serie title from the parent directory!
        #query += result

        # post-processing
        # we could already clean a bit the data here by solving it and comparing it to
        # each element we found, eg: remove all md which have an improbable episode number
        # such as 72 if some other valid episode number has been found, etc...

        self.emit(SIGNAL('finished'), query)
