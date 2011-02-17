#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2011 Nicolas Wack <wackou@gmail.com>
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


import SocketServer
import socket
import sys
import threading
import logging

PORT = 9999
CALLBACK = None

log = logging.getLogger('smewt.base.singleapplication')

class ActivationHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()

        if CALLBACK:
            CALLBACK()

        self.request.send('OK')


class ReusableSocketServer(SocketServer.TCPServer):
    allow_reuse_address = True


class SingleApplicationWatcher:
    def __init__(self):
        self.activateRunningInstance()

    def activateRunningInstance(self):
        self.running = False

        # Create the server, binding to localhost on port 9999
        try:
            log.info('Creating single app server on %s:%d' % ('localhost', PORT))
            if sys.platform == 'win32':
                # it looks like with reuse_address multiple processes can listen
                # on the same port on windows (python bug?)
                self.server = SocketServer.TCPServer(('localhost', PORT), ActivationHandler)
            else:
                self.server = ReusableSocketServer(('localhost', PORT), ActivationHandler)
            self.running = True
        except:
            # address already in use, activate running server and exit
            log.warning('Found already running instance, activate it')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', PORT))
            sock.send("activate")

            received = sock.recv(1024)
            log.warning('Activation status: %s' % received)
            sock.close()
            log.warning('Exiting...')
            sys.exit()

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        serverThread = threading.Thread(target = self.server.serve_forever)
        serverThread.setDaemon(True)
        serverThread.start()

    def shutdown(self):
        self.server.shutdown()

    def __del__(self):
        if self.running:
            self.shutdown()

