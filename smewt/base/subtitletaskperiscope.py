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
import guessit.language
import periscope
import os.path

import itertools
import logging

log = logging.getLogger('smewt.subtitletask')

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

        #ep.graph().display_graph()

        files = tolist(self.episode.get('files', []))
        if files:
            filepath = files[0].filename
        else:
            filepath = '%s %dx%02d %s' % (ep.series.title, ep.season, ep.episodeNumber, ep.get('title', ''))

        subs = subdl.listSubtitles(filepath, [self.language])

        for sub in subs :
            log.debug("Found a sub from %s in language %s, downloadable from %s" % (sub['plugin'], sub['lang'], sub['link']))

        # TODO: choose best subtitle smartly

        if not subs:
            raise SmewtException('Could not find any subs for %s' % self.episode)


        # FIXME: need to be fixed in periscope so that it can return the text directly, or at least let
        #        us choose where it needs to be written
        subpath = filepath.rsplit(".", 1)[0] + '.srt'
        if os.path.exists(subpath):
            os.rename(subpath, subpath + '.bak')

        sub = subdl.attemptDownloadSubtitle(subs, [self.language])
        if sub:
            result = open(sub["subtitlepath"]).read()
            os.remove(sub["subtitlepath"])
            log.debug('Successfully downloaded %s subtitle for %s' % (self.language, self.episode))
        else:
            raise SmewtException('Could not complete download for sub %s' % self.episode)

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

            languageMap = guessit.language.languageMap
            filetmpl = files[0].filename.rsplit('.', 1)[0] + '.' + languageMap[lang] + '%s.srt'

            filename = filetmpl % ''
            i = 2
            while os.path.exists(filename):
                filename = filetmpl % i
                i += 1

            if sys.platform != 'win32':
                subtext = subtext.replace('\r\n', '\n')

            open(filename, 'w').write(subtext)



        ############# OLD IMPLEMENTATION
        return

        languageMap = guessit.language.languageMap

        # find objects which don't have yet a subtitle of the desired language
        seriesEpisodes = set(tolist(self.series.episodes))
        currentSubs = self.database.find_all(node_type = Subtitle,
                                             valid_node = lambda x: x.metadata in seriesEpisodes,
                                             language = self.language)

        alreadyGood = set([ s.metadata for s in currentSubs ])

        episodes = [ ep for ep in seriesEpisodes if ep not in alreadyGood ]
        if not episodes:
            log.info('All videos already have subtitles!')

        subs = MemoryObjectGraph()

        for ep in episodes:
            try:
                # the following assumes we always have a single metadata object for this file
                videoFilename = ep.files.filename
                subFilename = os.path.splitext(videoFilename)[0] + '.%s.srt' % languageMap[self.language]

                # if file doesn't exist yet, try to download it
                if not os.path.isfile(subFilename):
                    possibleSubs = self.provider.getAvailableSubtitles(ep).find_all(language = self.language)
                    if not possibleSubs:
                        raise SubtitleNotFoundError('didn\'t find any possible subs...')

                    # we could do a more elaborate selection here if more than 1 result is returned
                    candidate = possibleSubs[0]
                    if len(possibleSubs) > 1:
                        log.warning('More than 1 possible subtitle found: %s', str(possibleSubs))
                        dists = [ (textutils.levenshtein(videoFilename, sub.title), sub) for sub in possibleSubs ]
                        candidate = sorted(dists)[0][1]
                        log.warning('Choosing %s' % candidate)

                    log.info('Trying to download subs for %s' % ep.files.filename)
                    subtext = self.provider.getSubtitle(candidate)

                    # write the subtitle in the appropriate file
                    # (here as well we might want to look at how many results we have (ie: movie
                    # spanning multiple CDs, etc...)
                    if self.subfile is not None:
                        with open(subFilename, 'w') as f:
                            f.write(subtext)
                        log.info('Found subtitle for %s' % ep.files.filename)

                else:
                    log.warning('\'%s\' already exists. Not overwriting it...' % subFilename)

                # update the found subs with this one
                sub = self.database.Subtitle(metadata = ep, language = self.language)
                subfile = self.database.Media(filename = subFilename, metadata = sub)

            except SubtitleNotFoundError, e:
                log.warning('subno: did not found any subtitle for %s: %s', str(video), str(e))

            except SmewtException, e:
                log.warning('se: did not found any subtitle for %s: %s' % (str(video), str(e)))


        log.debug('SubtitleTaskPeriscope: all done!')
