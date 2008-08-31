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
    def __init__(self, task, args, results):
        super(WorkerThread, self).__init__()
        self.task = task
        self.args = args
        self.results = results

        self.connect(self.task, SIGNAL('finished'),
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
    def launch(self, task, args):
        results = [ None ]
        t = WorkerThread(task, args, results)
        t.start()

        # hack to make sure the worker thread could enter its event loop
        QThread.msleep(100)

        task.start(args)
        t.wait()

        return results[0]


def allTests(testClass):
    return TestLoader().loadTestsFromTestCase(testClass)
