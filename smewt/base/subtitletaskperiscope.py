#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from __future__ import with_statement
from PyQt4.QtCore import SIGNAL, Qt, QObject
from pygoo import MemoryObjectGraph
from smewt.base import Media, Task, SmewtException, textutils
from smewt.base.utils import tolist
from smewt.media import Series, Subtitle, SubtitleNotFoundError
import periscope
import sys, os.path

import itertools
import logging

log = logging.getLogger('smewt.subtitletask')

import guessit.language
languageMap = guessit.language._language_map

# TODO: should be renamed SeriesSubtitleTask
class SubtitleTaskPeriscope(Task):
    """Tries to download a subtitle for the given episode. If force = True, it will
    download it and overwrite a previous subtitle.

    #episode is a dict with keys: 'series', 'season' and 'episodeNumber'.
    episode is an Episode instance

    TODO: should look at all the available subs, remove duplicates, and keep all those
    remaining, maybe numbered to distinguish them."""
    def __init__(self, episode, language, subfile = None, force = False):
        super(SubtitleTaskPeriscope, self).__init__()
        self.episode = episode
        self.language = language
        self.subfile = subfile
        self.force = force

        log.info('Creating SubtitleTaskPeriscope for episode %dx%02d from series: %s' % (episode['season'], episode['episodeNumber'], episode['series']))


    def downloadSubtitleText(self):
        subdl = periscope.Periscope()

        ep = self.episode
        epdesc = 'episode %dx%02d of %s' % (self.episode.season, self.episode.episodeNumber, self.episode.series.title)

        log.info('Trying to download subtitle for %s' % epdesc)

        files = tolist(self.episode.get('files', []))
        if files:
            filepath = files[0].filename
        else:
            filepath = '%s %dx%02d %s' % (ep.series.title, ep.season, ep.episodeNumber, ep.get('title', ''))

        subs = subdl.listSubtitles(filepath, [self.language])

        for sub in subs :
            log.debug("Found a sub from %s in language %s, downloadable from %s" % (sub['plugin'], sub['lang'], sub['link']))


        if not subs:
            raise SmewtException('Could not find any %s subs for %s' % (self.language, epdesc))

        # TODO: choose best subtitle smartly
        if len(subs) > 1:
            log.warning('Multiple subtitles found, trying to pick the best one...')

        # FIXME: need to be fixed in periscope so that it can return the text directly, or at least let
        #        us choose where it needs to be written
        subpath = filepath.rsplit(".", 1)[0] + '.srt'
        if os.path.exists(subpath):
            os.rename(subpath, subpath + '.bak')

        sub = subdl.attemptDownloadSubtitle(subs, [self.language])
        if sub:
            result = open(sub["subtitlepath"]).read()
            os.remove(sub["subtitlepath"])
            log.debug('Successfully downloaded %s subtitle for %s' % (self.language, epdesc))
        else:
            raise SmewtException(u'Could not complete download for sub of %s' % epdesc)

        if os.path.exists(subpath + '.bak'):
            os.rename(subpath + '.bak', subpath)

        return result


    def perform(self):
        subtext = self.downloadSubtitleText()

        if self.subfile is not None:
            if not os.path.isfile(self.subfile) or self.force:
                # TODO: instead of self.force, maybe write all of them but numbered
                with open(subFilename, 'w') as f:
                    f.write(subtext)
                log.info('Found subtitle for %s' % ep.files.filename)
            else:
                log.warning('\'%s\' already exists. Not overwriting it...' % subFilename)

        else:
            # find an appropriate filename
            files = tolist(self.episode.get('files', []))
            if not files:
                log.error('Cannot write subtitle file for %s because it doesn\'t have an attached file')

            filetmpl = files[0].filename.rsplit('.', 1)[0] + '.' + languageMap[self.language] + '%s.srt'

            filename = filetmpl % ''
            i = 2
            while os.path.exists(filename):
                filename = filetmpl % i
                i += 1

            if sys.platform != 'win32':
                subtext = subtext.replace('\r\n', '\n')

            open(filename, 'w').write(subtext)

            # update the found subs with this one
            db = self.episode.graph()
            sub = db.Subtitle(metadata = self.episode, language = self.language)
            subfile = db.Media(filename = filename, metadata = sub)

