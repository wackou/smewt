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



# filename- and network-related functions
import sys, os, os.path, fnmatch,  errno
from guessit.language import Language, guess_language, UNDETERMINED
from guessit.fileutils import split_path
from pygoo.utils import tolist, toresult
from smewt.base.smewtexception import SmewtException
import logging

log = logging.getLogger(__name__)


class SDict(dict):
    """Dictionary class that also allows read-only attribute-like access
    to the dictionary values."""
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except AttributeError:
            return self[attr]


# TODO: implement as NamedTuple
class MethodID(object):
    def __init__(self, filename, module, className, methodName):
        self.filename = filename
        self.module = module
        self.className = className
        self.methodName = methodName

    def __str__(self):
        return 'module: %s - class: %s - func: %s' % (self.module, self.className, self.methodName)

def callerid():
    f = sys._getframe(1)

    filename = f.f_code.co_filename
    module = ''
    className = ''

    try:
        module = f.f_locals['self'].__class__.__module__
        className = f.f_locals['self'].__class__.__name__
    except:
        pass

    methodName = f.f_code.co_name

    return MethodID(filename, module, className, methodName)

def currentPath():
    '''Returns the path in which the calling file is located.'''
    return os.path.dirname(os.path.join(os.getcwd(), sys._getframe(1).f_globals['__file__']))

def makedir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else: raise

def path(*args, **kwargs):
    p = os.path.join(*args)
    if kwargs.get('createdir', False):
        makedir(os.path.dirname(p))
    return p


def commonRoot(pathlist):
    if not pathlist:
        return []

    root = split_path(pathlist[0])
    for path in pathlist[1:]:
        for i, dir in enumerate(split_path(path)):
            try:
                if root[i] != dir:
                    root = root[:i]
                    break
            except IndexError:
                break
        else:
            root = root[:len(split_path(path))]

    return os.path.join(*root)

def parentDirectory(path):
    parentDir = split_path(path)[:-1]
    return os.path.join(*parentDir)


def extractText(subtext):
    """Take a subtitle text as input and remove the lines that start with a
    time code."""
    lines = [ l.strip() for l in subtext.split('\n') ]
    lines = [ l for l in lines if l and l[0] not in '0123456789' ]
    return '\n'.join(lines)


def readFile(filename):
    """Read a file from disk, and return it as a unicode string."""
    text = open(filename).read()
    try:
        text = unicode(text, 'utf-8')
    except UnicodeDecodeError:
        log.debug('Subtitle not utf-8, trying latin-1...')
        text = unicode(text, 'latin-1')
    except UnicodeDecodeError:
        log.warn('Error: can\'t find codec for decoding file: %s' % filename)
        raise

    return text


# TODO: Use enzyme for this
def guessCountryCodes(filename):
    '''Given a subtitle filename, tries to guess which languages it contains.
    As a subtitle file can contain multiple subtitles, this function returns a list
    of found languages.'''

    # try to guess language from filename
    langs = [ lang.lower() for lang in filename.split('.') ]

    if len(langs) >= 3:
        lang = Language(langs[-2].lower())
        if lang:
            return [ lang ]

    # try to autodetect the language using the content of the subtitle
    if langs[-1] in ('srt', 'ssa'):
        text = extractText(readFile(filename))
        lang = guess_language(text)
        if lang != UNDETERMINED:
            return [ lang ]

    # try to look inside the .idx, if it exists
    langs = set()
    if os.path.exists(filename[:-3] + 'idx'):
        lines = open(filename[:-3] + 'idx').readlines()
        for l in lines:
            if l[:3] == 'id:':
                langs.add(Language(l[4:6]))

    if langs:
        return list(langs)

    return [ Language('unknown') ]


def guessitToPygoo(guess):
    for lang in ('language', 'subtitleLanguage'):
        value = tolist(guess.get(lang))
        if len(value) > 1:
            guess[lang] = [ l.alpha2 for l in value ]
        elif value:
            guess[lang] = value[0].alpha2

    value = tolist(guess.get('date'))
    if len(value) > 1:
        guess['date'] = [ d.isoformat() for d in value ]
    elif value:
        guess['date'] = value[0].isoformat()

    return guess



def matchFile(filename, validFiles=['*']):
    for validFile in validFiles:
        # if validFile is a string pattern, do filename matching
        if isinstance(validFile, basestring):
            if fnmatch.fnmatch(filename, validFile):
                return True
        elif callable(validFile):
            # if it's a filter function, return whether a file should be considered
            if validFile(filename):
                return True
        else:
            raise SmewtException('Argument to utils.matchFiles is not a valid filter: %s' % validFile)

    return False


def dirwalk(directory, validFiles=['*'], recursive=True):
    """A generator that goes through all the files in the given directory that matches
    at least one of the patterns.

    Patterns can either be strings used for globbing or filter functions that return
    True if the file needs to be considered."""
    for root, dirs, files in os.walk(directory, followlinks=True):
        for f in files:
            filename = os.path.join(root, f)
            if matchFile(filename, validFiles):
                yield filename

        if recursive is False:
            break
