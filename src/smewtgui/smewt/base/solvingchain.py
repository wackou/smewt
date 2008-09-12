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

from PyQt4.QtCore import Qt, SIGNAL, QObject
from smewtexception import SmewtException
from workerthread import WorkerThread
import logging

class SolvingChain(QObject):
    def __init__(self, *args):
        super(SolvingChain, self).__init__()

        self.chain = args
        if not args:
            raise SmewtException('Tried to build an empty solving chain')

        # connect each element (guesser, solver) to the next
        for elem, next in zip(self.chain[:-1], self.chain[1:]):
            self.connect(elem, SIGNAL('finished'),
                         next.start, Qt.QueuedConnection)

        # connect the last solver's finished to the whole chain finish method
        self.connect(self.chain[-1], SIGNAL('finished'),
                     self.finished, Qt.QueuedConnection)


    def start(self, query):
        '''Launches the solving chain process asynchronously, eg: it returns
        immediately and will emit the signal 'finished' along with the result of
        it when done.'''
        self.chain[0].start(query)

    def launchAndWait(self, query):
        '''Launches the solving chain process synchronously, eg: it will only
        return when it has finished solving the chain. This method returns the
        result of the chain.'''
        results = [ None ]
        t = WorkerThread(self, query, results)
        t.start()

        # hack to make sure the worker thread could enter its event loop
        from PyQt4.QtCore import QThread
        QThread.msleep(100)

        self.start(query)
        t.wait()

        return results[0]

    def finished(self, result):
        if result.metadata:
            logging.info('Solving chain for file %s found metadata: %s', str(result.media[0]), str(result.metadata[0]))
        else:
            logging.info('Solving chain for file %s didn\'t find any metadata...', str(result.media[0]))

        self.emit(SIGNAL('finished'), result)
