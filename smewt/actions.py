#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008-2013 Nicolas Wack <wackou@smewt.com>
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

from smewt.base.utils import tolist, toresult
from smewt.base.subtitletask import SubtitleTask
from smewt.plugins import mplayer
from guessit.language import Language
import smewt
import os, sys, time
import subprocess
import logging

log = logging.getLogger(__name__)


def get_episodes_and_subs(language, series, season=None):
    db = smewt.SMEWTD_INSTANCE.database
    if season:
        episodes = set(ep for ep in tolist(series.episodes) if ep.season == int(season))
    else:
        episodes = set(tolist(series.episodes))

    subs = db.find_all(node_type='Subtitle',
                       # FIXME: we shouldn't have to go to the node, but if we don't, the valid_node lambda doesn't return anything...
                       valid_node=lambda x: toresult(list(x.metadata)) in set(ep.node for ep in episodes),
                       language=language)
    return episodes, subs



def get_subtitles(media_type, title, season=None, language=None):
    db = smewt.SMEWTD_INSTANCE.database
    language = language or db.config.get('subtitleLanguage') or 'en'

    if media_type == 'episode':
        series = db.find_one('Series', title=title)
        episodes, subs = get_episodes_and_subs(language, series, season)

        already_good = set(s.metadata for s in subs)

        episodes = episodes - already_good

        if episodes:
            subtask = SubtitleTask(episodes, language)
            smewt.SMEWTD_INSTANCE.taskManager.add(subtask)
        else:
            log.info('All episodes already have %s subtitles!' % Language(language).english_name)

    elif media_type == 'movie':
        movie = db.find_one('Movie', title=title)

        # check if we already have it
        for sub in tolist(movie.get('subtitles')):
            if sub.language == language:
                log.info('Movie already has a %s subtitle' % Language(language).english_name)
                return

        subtask = SubtitleTask(movie, language)
        smewt.SMEWTD_INSTANCE.taskManager.add(subtask)


    else:
        log.error('Don\'t know how to fetch subtitles for type: %s' % media_type)




def _play(files, subs):
    # launch external player
    args = files
    subs = subs + [None] * (len(files) - len(subs))

    # if we have mplayer installed, use it with subtitles support
    if os.system('which mplayer') == 0:
        action = 'mplayer'
        args = []
        for video, subfile in zip(files, subs):
            args.append(video)
            if subfile:
                args += [ '-sub', subfile ]

        log.info('launching %s with args = %s' % (action, str(args)))
        return mplayer.play(args)

    # RaspberryPi: use omxplayer
    if os.system('which omxplayer') == 0:
        action = 'omxplayer'
        args = []
        for video, subfile in zip(files, subs):
            args.append(video)
            if subfile:
                args += [ '-sub', subfile ]

        log.info('launching %s with args = %s' % (action, str(args)))
        return mplayer.play(args)


    if sys.platform == 'linux2':
        action = 'xdg-open'
        # FIXME: xdg-open only accepts 1 argument, this will break movies split in multiple files...
        args = args[:1]

        # if we have smplayer installed, use it with subtitles support
        if os.system('which smplayer') == 0:
            action = 'smplayer'
            args = [ '-fullscreen', '-close-at-end' ]
            for video, subfile in zip(files, subs):
                args.append(video)
                if subfile:
                    args += [ '-sub', subfile ]

    elif sys.platform == 'darwin':
        action = 'open'

    elif sys.platform == 'win32':
        action = 'open'


    log.info('launching %s with args = %s' % (action, str(args)))
    subprocess.call([action]+args)



def play_video(metadata, sublang=None):
    # FIXME: this should be handled properly with media player plugins

    # files should be a list of (Metadata, sub), where sub is possibly None
    # then we would look into the available graphs where such a Metadata has files,
    # and choose the one on the fastest media (ie: local before nfs before tcp)
    # it should also choose subtitles the same way, so we could even imagine reading
    # the video from one location and the subs from another

    # find list of all files to be played
    # returns a list of (video_filename, sub_filename)

    if sublang:
        msg = 'Playing %s with %s subtitles' % (metadata, Language(sublang).english_name)
    else:
        msg = 'Playing %s with no subtitles' % metadata
    log.info(msg)

    # FIXME: we assume that sorting alphanumerically is good enough, but that is
    #        not necessarily the case...
    #        we should also look whether the file also has the 'cdNumber' attribute
    files = tolist(metadata.get('files'))
    files = sorted(files, key=lambda f: f.get('filename'))

    if sublang is not None:
        sublang = Language(sublang)

    for sub in tolist(metadata.get('subtitles')):
        if sub.language == sublang:
            subs = sorted(tolist(sub.get('files')), key=lambda f: f.get('filename'))
            break
    else:
        subs = [None]*len(files)


    # update last viewed info
    metadata.lastViewed = time.time()

    _play([ f.filename for f in files],
          [ s.filename for s in subs if s ])


def play_file(filename):
    _play([filename], [None])
