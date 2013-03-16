#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2013 Nicolas Wack <wackou@smewt.com>
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

from smewt.base import SmewtException
from threading import Thread
import subprocess
import logging

log = logging.getLogger(__name__)

p = None
video_info = ''
pos = 0.0

# list of lines output on stdout by the mplayer process
STDOUT = []

# memory for stdout last (possibly incomplete) line
_stdout = ''

variant = 'undefined'

def detect():
    global variant

    def is_exe(cmd):
        p = subprocess.Popen(['which', cmd], stdout=subprocess.PIPE)
        p.communicate()
        return p.returncode == 0

    if is_exe('omxplayer'):
        log.info('Video player: detected omxplayer (RaspberryPi)')
        variant = 'omxplayer'
    elif is_exe('mplayer'):
        log.info('Video player: detected mplayer')
        variant = 'mplayer'
    else:
        log.info('Video player: mplayer not detected, video controls will not be available...')

detect()

def _send_command(cmd):
    p.stdin.write(cmd)
    log.debug('%s cmd: %s', variant, cmd)

def send_command(cmd):
    try:
        return _send_command(cmd)
    except:
        log.warning('Could not connect to %s to execute command: %s', variant, cmd)


def _readsome(p):
    return p.stdout.readline(512)

def _run(cmd=None, args=None):
    global p, video_info, pos, STDOUT, _stdout
    command = []
    if cmd:
        command.extend(cmd.split(' '))
    if args:
        command.extend(args)

    if p is not None:
        raise RuntimeError('%s is already running!' % variant)

    STDOUT = []
    _stdout = ''
    has_run = False

    log.debug('Running: %s', command)

    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    l = _readsome(p)

    while l:
        l = _stdout + l

        info_lines = [ # mplayer
                       'VIDEO:', 'AUDIO:',
                       # omxplayer
                       'Video codec ', 'Audio codec ', 'file : ' ]

        for info in info_lines:
            if l.startswith(info):
                log.debug('%s info: %s', variant, l.strip())
                video_info += l
                _stdout = ''
                break

        else:
            if '\r' in l:
                for ll in l.split('\r')[:-1]:
                    ll = ll.strip()
                    if ll.startswith('A:'):
                        # mplayer
                        try:
                            pos = float(ll.split()[1])
                            has_run = True
                        except (IndexError, ValueError):
                            log.debug('wrong pos info: %s', ll)
                            pass
                    elif ll.startswith('V :'):
                        # omxplayer
                        try:
                            pos = float(ll.split()[7])
                            has_run = True
                        except (IndexError, ValueError):
                            log.debug('wrong pos info: %s', ll)
                            pass
                    else:
                        log.debug('%s stdout: %s', variant, ll)
                        STDOUT.append(ll)

                _stdout = l.split('\r')[-1]

            else:
                log.debug('%s stdout: %s', variant, l.strip())
                STDOUT.append(l.strip())
                _stdout = ''


        l = _readsome(p)

    pos = 0.0
    p = None
    log.info('%s process ended', variant)

    if variant in ['mplayer', 'omxplayer'] and not has_run:
        raise SmewtException('Error while playing file: %s' % '\n'.join(STDOUT))


def play(files, subs=None, opts=None):
    log.info('%s play - opts: %s', variant, opts)
    if p is not None:
        raise SmewtException('%s is already running!' % variant)

    opts = opts or []
    if isinstance(opts, basestring):
        opts = opts.split(' ') # TODO: isn't there some shell args quoting function?
    subs = subs or [None] * len(files)
    # make sure subs is as long as args so as to not cut it when zipping them together
    subs = subs + [None] * (len(files) - len(subs))

    args = list(opts)

    if variant == 'mplayer':
        for video, subfile in zip(files, subs):
            args.append(video)
            if subfile:
                args += [ '-sub', subfile ]
    elif variant == 'omxplayer': # RaspberryPi
        args.append('-s') # needed for getting the video pos info
        for video, subfile in zip(files, subs):
            args.append(video)
            if subfile:
                args += [ '--subtitles', subfile ]

    # TODO: check if we don't die because of a timeout in the wsgi request
    return _run(variant, args)
    """
    def run():
        _run(variant, args)

    t = Thread(target=run)
    t.daemon = True
    t.start()
    """

def pause():
    log.info('%s pause', variant)
    send_command(' ')


def stop():
    global pos
    log.info('%s stop', variant)
    send_command('q')
    pos = 0.0


def fast_back():
    log.info('%s fast back', variant)
    send_command('\x1B[B') # down

def back():
    log.info('%s back', variant)
    send_command('\x1B[D') # left

def forward():
    log.info('%s forward', variant)
    send_command('\x1B[C') # right

def fast_forward():
    log.info('%s fast forward', variant)
    send_command('\x1B[A') # up
