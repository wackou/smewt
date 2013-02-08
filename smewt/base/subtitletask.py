#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008-2012 Nicolas Wack <wackou@smewt.com>
# Copyright (c) 2008 Ricard Marxer <rikrd@smewt.com>
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

from smewt.base import Task, SmewtException, Metadata
from smewt.base.utils import tolist, smewtUserPath
from smewt.media import Movie, Episode
from guessit import Language
from subliminal.core import get_defaults, key_subtitles, create_download_tasks
from subliminal.language import language_list
import subliminal
import sys, os.path
import logging

log = logging.getLogger(__name__)



def findAvailableFilename(template):
    i = 1
    filename = template % ''
    while os.path.exists(filename):
        i += 1
        filename = template % i

    return filename


class SubtitleTask(Task):
    """Tries to download a list of subtitles for the given episodes or movies.
    If force = True, it will download it and overwrite previous subtitles.

    metadata is the list of objects for which to download the subtitle (Movie or Episode).
    """

    def __init__(self, metadata, language, force=False, services=None):
        super(SubtitleTask, self).__init__()
        if isinstance(metadata, Metadata):
            metadata = [ metadata ]
        self.metadata = metadata
        self.language = Language(language)
        self.services = services
        self.force = force
        self.description = 'Downloading multiple %s subtitles' % self.language.english_name

        log.info('Creating SubtitleTask (%s) for %s' % (language, list(metadata)[0].get('title', '?')))


    def downloadSubtitles(self, requested):
        # list all available subtitles
        lang = self.language.alpha2
        with subliminal.Pool(4) as p:
            paths, languages, services, order = get_defaults(requested.keys(),
                                                             [lang], self.services, None,
                                                             languages_as=language_list)
            cache_dir = smewtUserPath('subliminal_cache', createdir=True)

            subs = p.list_subtitles(requested.keys(), languages,
                                    services = services,
                                    cache_dir = cache_dir)

            if not subs:
                raise SmewtException('No subtitles could be found for files: %s' % requested.keys())

            # set the correct filenames for the subs to be downloaded
            for video, subs_candidates in subs.items():
                subtitleFilename = requested[video.path]
                for s in subs_candidates:
                    s.path = subtitleFilename

            # pick the best subtitles from this list
            # taken from subliminal/async.py
            for video, subtitles in subs.iteritems():
                subtitles.sort(key=lambda s: key_subtitles(s, video, languages, services, order), reverse=True)

            # download the subtitles
            tasks = create_download_tasks(subs, languages, multi=False)
            return p.consume_task_list(tasks)


    def perform(self):
        requested = {}
        for obj in self.metadata:
            if not obj.isinstance(Episode) and not obj.isinstance(Movie):
                log.warning('Unknown type for downloading subtitle: %s' % obj.__class__.__name__)
                continue

            files = tolist(obj.get('files', []))
            if not files:
                log.warning("Cannot download subtitle for %s because it doesn't have an attached file" % obj.niceString())
                continue

            # find an appropriate filename
            videoFilename = files[0].filename

            filetmpl = '%s.%s' % (os.path.splitext(videoFilename)[0],
                                  self.language.english_name) + '%s.srt'
            subFilename = findAvailableFilename(filetmpl)

            requested[videoFilename] = subFilename

        if not requested:
            raise SmewtException('Invalid list of objects for which to download subtitles')

        # download subtitles
        self.downloadSubtitles(requested)

        # validate the subtitles
        for videoFilename, subFilename in requested.items():
            # make sure the files actually exist on disk
            if not os.path.exists(subFilename):
                log.warning('Could not download subtitle for file %s' % videoFilename)
                continue

            # normalize subtitle file end-of-lines
            if sys.platform != 'win32':
                with open(subFilename) as subfile:
                    subtext = subfile.read().replace('\r\n', '\n')
                with open(subFilename, 'w') as subfile:
                    subfile.write(subtext)

            # update the database with the found subs
            db = list(self.metadata)[0].graph()
            for obj in self.metadata:
                filenames = [ f.filename for f in tolist(obj.get('files', [])) ]
                if videoFilename in filenames:
                    # FIXME: the following 2 lines should happen in a transaction
                    sub = db.Subtitle(metadata = obj, language = self.language.alpha2)
                    subfile = db.Media(filename = subFilename, metadata = sub)
                    break
            else:
                log.error('Internal error: downloaded subfile for non-requested metadata')
