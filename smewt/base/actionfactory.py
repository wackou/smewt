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

from PyQt4.QtCore import SIGNAL, QObject
from smewtexception import SmewtException
from mediaobject import Media, Metadata
from subtitletask import SubtitleTask
from smewt.media import Series
import sys, time, logging


log = logging.getLogger('smewt.base.actionfactory')

# Singleton pattern found at http://code.activestate.com/recipes/66531/
class Singleton(object):
    def __new__(cls):
        if not '_the_instance' in cls.__dict__:
            cls._the_instance = object.__new__(cls)
        return cls._the_instance


# TODO: actions in the ActionFactory should be registered as plugins that
# can provide certain types of service, ie: getsubtitles action may be filled
# by tvsubtitles, opensubtitles, etc...
class ActionFactory(Singleton):
    def __init__(self):
        self.subtitleProviders = []
        self.registerPlugins()

    def registerPlugins(self):
        # subs += opensubtitles
        from smewt.media.subtitle.subtitle_tvsubtitles_provider import TVSubtitlesProvider
        self.subtitleProviders.append(TVSubtitlesProvider())

    def dispatch(self, mainWidget, surl):
        if surl.actionType == 'play':
            if sys.platform == 'linux2':
                action = 'smplayer'
                args = [ '-fullscreen', '-close-at-end' ]

                nfile = 1
                while 'filename%d' % nfile in surl.args:
                    filename = surl.args['filename%d' % nfile]
                    args.append(filename)

                    # update last viewed info
                    media = mainWidget.smewtd.database.find_one(Media, filename = filename)
                    media.metadata.lastViewed = time.time()

                    if 'subtitle%d' % nfile in surl.args:
                        args += [ '-sub', surl.args['subtitle%d' % nfile] ]

                    nfile += 1

            elif sys.platform == 'darwin':
                action = 'open'
                args = []
                nfile = 1
                while 'filename%d' % nfile in surl.args:
                    filename = surl.args['filename%d' % nfile]
                    args.append(filename)
                    nfile += 1

            log.debug('launching %s with args = %s' % (action, str(args)))
            mainWidget.externalProcess.startDetached(action, args)

        elif surl.actionType == 'getsubtitles':
            title = surl.args['title']
            language = surl.args['language']

            for provider in self.subtitleProviders:
                subTask = SubtitleTask(mainWidget.smewtd.database, provider, title, language)
                mainWidget.smewtd.taskManager.add(subTask)

        else:
            raise SmewtException('Unknown action type: %s' % surl.actionType)
