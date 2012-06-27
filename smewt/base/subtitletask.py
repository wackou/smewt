#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008-2012 Nicolas Wack <wackou@gmail.com>
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
from smewt.base.utils import tolist, smewtUserPath
from smewt.media import Movie, Series, Episode, Subtitle
import subliminal
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


    def downloadSubtitle(self, videoFilename, subtitleFilename):
        # list all available subtitles
        lang = self.language.alpha2
        services = None # ['opensubtitles'] # FIXME: temporary for debugging, faster than querying all the services
        subs = subliminal.list_subtitles(videoFilename, [lang],
                                         services = services,
                                         cache_dir = smewtUserPath('subliminal_cache',
                                                                   createdir=True))

        if not subs:
            raise SmewtException('No subtitles could be found for file: %s' % videoFilename)

        video, subs = subs.items()[0]

        # set the correct filenames for the subs to be downloaded
        for s in subs:
            s.path = subtitleFilename

        # TODO: pick the best subtitle from this list

        # download the subtitle
        task = subliminal.tasks.DownloadTask(videoFilename, subs)
        return subliminal.core.consume_task(task)


    def findAvailableFilename(self, template):
        i = 1
        filename = template % ''
        while os.path.exists(filename):
            i += 1
            filename = template % i

        return filename


    def perform(self):
        obj = self.metadata

        if not obj.isinstance(Episode) and not obj.isinstance(Movie):
            raise SmewtException('Unknown type for downloading subtitle: %s' % obj.__class__.__name__)

        files = tolist(self.metadata.get('files', []))
        if not files:
            raise SmewtException('Cannot write subtitle file for %s because it doesn\'t have an attached file')

        # find an appropriate filename
        videoFilename = files[0].filename
        filetmpl = '%s.%s' % (os.path.splitext(videoFilename)[0],
                              self.language.english_name) + '%s.srt'

        subFilename = self.findAvailableFilename(filetmpl)
        if self.subfile is not None:
            if not os.path.isfile(self.subfile) or self.force:
                subFilename = self.subfile
            else:
                log.warning('%s already exists. Not overwriting it...' % self.subfile)
                return

        # download subtitle
        result = self.downloadSubtitle(videoFilename, subFilename)

        if not result:
            raise SmewtException('Could not download subtitle for %s' % videoFilename)

        # TODO: make sure the file actually exists on disk
        if not os.path.exists(subFilename):
            raise SmewtException('There seems to have been a problem during the subtitle download')

        # normalize subtitle file end-of-lines
        if sys.platform != 'win32':
            subtext = open(subFilename).read().replace('\r\n', '\n')
            with open(subFilename, 'w') as subfile:
                subfile.write(subtext)

        # update the found subs with this one
        db = self.metadata.graph()
        # FIXME: the following 2 lines should happen in a transaction
        sub = db.Subtitle(metadata = self.metadata, language = self.language.alpha2)
        subfile = db.Media(filename = subFilename, metadata = sub)
