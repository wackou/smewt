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

import os, os.path, subprocess, logging
import threading, time

log = logging.getLogger('smewt.plugins.amulecommand')

class ProcessTimeout(threading.Thread):
    '''Class that checks that the given process doesn't run for longer than a given number of seconds.'''
    def __init__(self, process, maxSeconds = 5):
        super(ProcessTimeout, self).__init__()
        self.process = process
        self.maxSeconds = maxSeconds

    def run(self):
        secs = 0
        while self.process.poll() is None:
            time.sleep(1)
            secs += 1
            if secs >= self.maxSeconds:
                # need to kill process, starting from python 2.6 we can use process.terminate()
                # meanwhile, let's just kill it by hand
                subprocess.Popen(['kill', str(self.process.pid)])
                return


def recreateAmuleRemoteConf():
    amuleConf = os.path.join(os.environ['HOME'], '.aMule', 'amule.conf')
    amulecmd = os.path.join('/usr', 'bin', 'amulecmd')
    if os.path.exists(amuleConf) and os.path.exists(amulecmd):
        cmd = [ amulecmd, '--create-config-from=' + amuleConf ]
        subprocess.Popen(cmd)
    else:
        log.warning('AmuleCommand: you need amule and amulecmd to be installed for aMule integration...')
        log.warning('AmuleCommand: on Debian/Ubuntu systems you can find the amulecmd in the "amule-utils" package')

# try to regenerate remote.conf when we import that module
recreateAmuleRemoteConf()

class AmuleCommand():
    def __init__(self):
        # message by default if the amulecmd process gets killed
        self.errmsg = "aMule doesn't appear to be running..."

    def download(self, ed2kLink):
        cmd = [ 'amulecmd', '--command=Add %s' % ed2kLink ]
        amuleProc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        ProcessTimeout(amuleProc, maxSeconds = 5).start()
        amuleReply, _ = amuleProc.communicate()

        print 'amule said:', amuleReply
        errheader = ' > Request failed with the following error: '
        errmsg = None
        for l in amuleReply.split('\n'):
            if l.startswith(errheader):
                self.errmsg = l[len(errheader):].strip()

        success = '> Operation was successful.' in amuleReply
        if success:
            return (True, None)
        else:
            return (False, self.errmsg)
