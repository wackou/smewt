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

from smewt.base import GraphAction, Media, Metadata, SmewtException
from smewt.media import Movie
from smewt.guessers.guesser import Guesser
from smewt.base import utils, textutils
import re
import logging

log = logging.getLogger('smewt.guessers.moviefilename')


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
        return filename, md


'''
def VideoFilename(filename):
    parts = textutils.cleanString(filename).split()

    found = {} # dictionary of identified named properties to their index in the parts list

    # heuristic 1: find VO, sub FR, etc...
    for i, part in enumerate(parts):
        if matchRegexp(part, [ 'VO', 'VF' ]):
            found = { ('audio', 'VO'): i }

    # heuristic 2: match video size
    #rexp('...x...') with x > 200  # eg: (720, 480) -> property format = 16/9, etc...

    # we consider the name to be what's left at the beginning, before any other identified part
    # (other possibility: look at the remaining zones in parts which are not covered by any identified props, look for the first one, or the biggest one)
    name = ' '.join(parts[:min(found.values())])
'''

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
    remove = [ '[', ']', '(', ')', '{', '}' ]
    for rem in remove:
        filename = filename.replace(rem, ' ')

    name = filename.split(' ')


    properties = { 'format': [ 'DVDRip', 'HDDVD', 'HDDVDRip', 'BDRip', 'R5', 'HDRip', 'DVD', 'Rip' ],
                   'container': [ 'avi', 'mkv', 'ogv', 'wmv', 'mp4', 'mov' ],
                   'screenSize': [ '720p' ],
                   'videoCodec': [ 'XviD', 'DivX', 'x264', 'Rv10' ],
                   'audioCodec': [ 'AC3', 'DTS', 'He-AAC', 'AAC-He', 'AAC' ],
                   'language': [ 'english', 'eng',
                                 'spanish', 'esp',
                                 'french', 'fr',
                                 'italian', # no 'it', too common a word in english
                                 'vo', 'vf'
                                 ],
                   'releaseGroup': [ 'ESiR', 'WAF', 'SEPTiC', '[XCT]', 'iNT', 'PUKKA', 'CHD', 'ViTE', 'DiAMOND', 'TLF',
                                     'DEiTY', 'FLAiTE', 'MDX', 'GM4F', 'DVL', 'SVD', 'iLUMiNADOS', ' FiNaLe', 'UnSeeN' ],
                   'other': [ '5ch', 'PROPER', 'REPACK', 'LIMITED', 'DualAudio', 'iNTERNAL', 'Audiofixed',
                              'classic', # not so sure about this one, could appear in a title
                              'ws', # widescreen
                              'SE', # special edition
                              # TODO: director's cut
                              ],
                   }

    # ensure they're all lowercase
    for prop, value in properties.items():
        properties[prop] = [ s.lower() for s in value ]


    # to try to guess what part of the filename is the movie title, we only keep as
    # possible title the first characters of the filename up to the leftmost metadata
    # element we found, no more
    minIdx = len(name)

    # get specific properties
    for prop, value in properties.items():
        for part in name:
            if part.lower() in value:
                md[prop] = part
                minIdx = min(minIdx, name.index(part))


    # get year
    def validYear(year):
        try:
            return int(year) > 1920 and int(year) < 2015
        except ValueError:
            return False


    for part in name:
        year = textutils.stripBrackets(part)
        if validYear(year):
            md['year'] = int(year)
            minIdx = min(minIdx, name.index(part))

    # remove ripper name
    for by, who in zip(name[:-1], name[1:]):
        if by.lower() == 'by':
            md['ripper'] = who
            minIdx = min(minIdx, name.index(by))

    # subtitles
    for sub, lang in zip(name[:-1], name[1:]):
        if sub.lower() == 'sub':
            md['subtitleLanguage'] = lang
            minIdx = min(minIdx, name.index(sub))

    # get CD number (if any)
    cdrexp = re.compile('[Cc][Dd]([0-9]+)')
    for part in name:
        try:
            md['cdNumber'] = int(cdrexp.search(part).groups()[0])
            minIdx = min(minIdx, name.index(part))
        except AttributeError:
            pass

    name = ' '.join(name[:minIdx])
    minIdx = len(name)

    # last chance on the full name: try some popular regexps
    general = [ '(?P<dircut>director\'s cut)',
                '(?P<edition>edition collector)' ]
    websites = [ 'sharethefiles.com' ]
    websites = [ '(?P<website>%s)' % w.replace('.', ' ') for w in websites ] # dots have been previously converted to spaces
    rexps = general + websites

    matched = textutils.matchAllRegexp(name, rexps)
    for match in matched:
        for key, value in match.items():
            minIdx = min(minIdx, name.find(value))

    name = name[:minIdx]

    # try website names
    # TODO: generic website url guesser
    websites = [ 'sharethefiles.com' ]


    # return final name as a guess for the movie title
    md['title'] = name
    return md


class MovieFilename(GraphAction):

    supportedTypes = [ 'video', 'subtitle' ]

    def __init__(self):
        super(MovieFilename, self).__init__()

    def canHandle(self, query):
        media = query.find_one(Media)
        if media.type() not in ('video', 'subtitle'):
            raise SmewtException("%s: can only handle video or subtitle media objects: %s" % (self.__class__.__name__, media.filename))

    def perform(self, query):
        self.checkValid(query)
        media = query.find_one(node_type = Media)

        movie = cleanMovieFilename(media.filename)

        #log.info('Found filename information from %s: %s' % (media.filename, movie))

        media.matches = query.Movie(**movie)
        return query
