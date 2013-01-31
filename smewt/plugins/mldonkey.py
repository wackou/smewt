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

import telnetlib
import logging

log = logging.getLogger(__name__)

HOST = 'localhost'
PORT = 4000

def send_command(cmd):
    try:
        tn = telnetlib.Telnet(HOST, PORT)
        tn.read_very_eager()
        tn.write(cmd+'\nq\n')
        response = '\n'.join(tn.read_all().split('\n')[7:-2])
        tn.close()

        log.debug('mldonkey cmd: %s' % cmd)
        log.debug('response:\n%s' % response)
        return response

    except:
        log.error('Could not connect to %s:%d to execute command: %s' % (HOST, PORT, cmd))


def download(ed2k_link):
    result = send_command('dllink ' + ed2k_link)
    if not result:
        return False, 'no connect'

    success = ('Added link' in result) or ('already' in result)
    return success, result
