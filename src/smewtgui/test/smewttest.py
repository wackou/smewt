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

from unittest import *
from unittest import TestCase as BaseTestCase
from PyQt4.QtCore import SIGNAL, QThread
import yaml, logging

class WorkerThread(QThread):
    def __init__(self, actuator, signal, query, results):
        super(WorkerThread, self).__init__()
        self.actuator = actuator
        self.query = query
        self.results = results

        self.connect(self.actuator, SIGNAL(signal),
                     self.finished)

    def run(self):
        logging.debug('Starting worker thread event loop...')
        self.exec_()
        logging.debug('Worker thread finished running')

    def finished(self, result):
        logging.debug('Worker thread received finished signal')
        self.results[0] = result
        self.quit()


class TestCase(BaseTestCase):
    def launchGuesser(self, guesser, query):
        results = [ None ]
        t = WorkerThread(guesser, 'guessFinished', query, results)
        t.start()

        # hack to make sure the worker thread could enter its event loop
        QThread.msleep(100)

        guesser.guess(query)
        t.wait()

        return results[0]

    def launchSolver(self, solver, query):
        results = [ None ]
        t = WorkerThread(solver, 'solveFinished', query, results)
        t.start()

        # hack to make sure the worker thread could enter its event loop
        QThread.msleep(100)

        solver.solve(query)
        t.wait()

        return results[0]



def allTests(testClass):
    return TestLoader().loadTestsFromTestCase(testClass)
