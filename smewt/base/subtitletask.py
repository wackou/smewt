#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008-2011 Nicolas Wack <wackou@gmail.com>
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from smewt.base import Task, SmewtException
from smewt.base.utils import tolist
from smewt.media import Movie, Series, Episode, Subtitle
import periscope
import sys, os.path
import logging

log = logging.getLogger('smewt.subtitletask')

from guessit import Language


class SubtitleTask(Task):
    """Tries to download a subtitle for the given episode or movie. If
    force = True, it will download it and overwrite a previous subtitle.

    metadata is the object for which to download the subtitle (Movie or Episode).

    TODO: should look at all the available subs, remove duplicates, and keep all those
    remaining, maybe numbered to distinguish them."""
    def __init__(self, metadata, language, subfile = None, force = False):
        super(SubtitleTask, self).__init__()
        self.metadata = metadata
        self.language = Language(language)
        self.subfile = subfile
        self.force = force
        self.description = 'Downloading subtitle for %s' % metadata.niceString()

        log.info('Creating SubtitleTask for %s' % metadata)


    def downloadPeriscopeSubtitleText(self, filepath, desc):
        subdl = periscope.Periscope()
        #subdl.pluginNames = [ 'Addic7ed' ]

        log.info('Trying to download %s subtitle for %s' % (self.language.english_name(), desc))

        subs = subdl.listSubtitles(filepath, [self.language.lng2()])

        if not subs:
            raise SmewtException('Could not find any %s subs for %s' % (self.language.english_name(), desc))

        for sub in subs :
            log.debug("Found a sub from %s in language %s, downloadable from %s" % (sub['plugin'], sub['lang'], sub['link']))


        # TODO: choose best subtitle smartly
        if len(subs) > 1:
            log.warning('Multiple subtitles found, trying to pick the best one...')


        sub = subdl.attemptDownloadSubtitleText(subs, [self.language.lng2()])
        if sub:
            result = sub["subtitletext"]
            log.debug('Successfully downloaded %s subtitle for %s' % (self.language.english_name(), desc))
        else:
            raise SmewtException(u'Could not complete download for sub of %s' % desc)

        return result


    def downloadEpisodeSubtitleText(self):
        ep = self.metadata
        desc = 'episode %dx%02d of %s' % (ep.season, ep.episodeNumber, ep.series.title)

        files = tolist(ep.get('files', []))
        if files:
            filepath = files[0].filename
        else:
            filepath = '%s %dx%02d %s' % (ep.series.title, ep.season, ep.episodeNumber, ep.get('title', ''))

        return self.downloadPeriscopeSubtitleText(filepath, desc)


    def downloadMovieSubtitleText(self):
        desc = 'movie ' + self.metadata.title

        files = tolist(self.metadata.get('files', []))
        if files:
            filepath = files[0].filename
        else:
            filepath = '%s.avi' % self.metadata.title

        return self.downloadPeriscopeSubtitleText(filepath, desc)


    def perform(self):
        if self.metadata.isinstance(Episode):
            subtext = self.downloadEpisodeSubtitleText()
        elif self.metadata.isinstance(Movie):
            subtext = self.downloadMovieSubtitleText()
        else:
            raise SmewtException('Unknown type for downloading subtitle: %s' % self.metadata.__class__.__name__)

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
            files = tolist(self.metadata.get('files', []))
            if not files:
                log.error('Cannot write subtitle file for %s because it doesn\'t have an attached file')

            filetmpl = files[0].filename.rsplit('.', 1)[0] + '.' + self.language.english_name() + '%s.srt'

            filename = filetmpl % ''
            i = 2
            while os.path.exists(filename):
                filename = filetmpl % i
                i += 1

            if sys.platform != 'win32':
                subtext = subtext.replace('\r\n', '\n')

            open(filename, 'w').write(subtext)

            # update the found subs with this one
            db = self.metadata.graph()
            sub = db.Subtitle(metadata = self.metadata, language = self.language.lng2())
            subfile = db.Media(filename = filename, metadata = sub)

