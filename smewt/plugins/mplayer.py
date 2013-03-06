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

from threading import Thread
import subprocess
import logging

log = logging.getLogger(__name__)

p = None
video_info = ''
pos = 0.0
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
    elif is_exe('smplayer'):
        log.info('Video player: detected smplayer')
        variant = 'smplayer'
    elif is_exe('mplayer'):
        log.info('Video player: detected mplayer')
        variant = 'mplayer'
    else:
        log.info('Video player: mplayer not detected, video controls will not be available...')

detect()

def _send_command(cmd):
    p.stdin.write(cmd)
    log.debug('mplayer cmd: %s' % cmd)

def send_command(cmd):
    try:
        return _send_command(cmd)
    except:
        log.warning('Could not connect to mplayer to execute command: %s' % cmd)


def _run(cmd=None, args=None):
    global p, video_info, pos, _stdout
    command = []
    if cmd:
        command.extend(cmd.split(' '))
    if args:
        command.extend(args)
    p = subprocess.Popen(command,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)

    l = True
    while l:
        l = p.stdout.readline(1024)
        #p.stderr.readline(1024)
        if l.startswith('VIDEO:'):
            video_info += l
        elif l.startswith('AUDIO:'):
            video_info += l
        else:
            for ll in (_stdout + l).split('\r')[:-1]:
                if ll.startswith('A:'):
                    # mplayer
                    try:
                        pos = float(ll.strip().split()[1])
                    except (IndexError, ValueError):
                        pass
                elif ll.startswith('V :'):
                    # omxplayer
                    try:
                        pos = float(ll.strip().split()[2]) / 1e6
                    except (IndexError, ValueError):
                        pass

            _stdout = l.split('\r')[-1]

    pos = 0.0
    log.info('mplayer process ended')



def play(args):
    log.info('mplayer play: %s' % args)

    def run():
        _run(variant, args)

    t = Thread(target=run)
    t.daemon = True
    t.start()

def pause():
    log.info('mplayer pause')
    send_command(' ')


def stop():
    global pos
    log.info('mplayer stop')
    send_command('q')
    pos = 0.0


def fast_back():
    log.info('mplayer fast back')
    send_command('\x1B[B') # down

def back():
    log.info('mplayer back')
    send_command('\x1B[D') # left

def forward():
    log.info('mplayer forward')
    send_command('\x1B[C') # right

def fast_forward():
    log.info('mplayer fast forward')
    send_command('\x1B[A') # up
