#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from __future__ import with_statement
from smewtexception import SmewtException
from Queue import Queue
from threading import Thread, Lock
import time
import logging

log = logging.getLogger('smewt.base.taskmanager')

class Task(object):
    def __init__(self, priority = 5):
        self.priority = priority

    def perform(self):
        """All tasks should implement this function, which should perform the actual task.

        No data is passed to this method. All the necessary task data should be given in the constructor.

        This method shouldn't return anything on success, and raise an exception in case of failure.
        It can have side effects though, such as updating the global collection for instance. In this case,
        the collection needs to be passed as argument to the constructor."""
        raise NotImplementedError


def worker(queue):
    while True:
        try:
            (_, _), task = queue.get()
            # TODO: need to have timeout on the tasks, eg: 5 seconds
            task.perform()
        except SmewtException, e:
            log.warning('TaskManager: task failed with error: %s' % e)
        except TypeError, e:
            # to avoid errors when the program exits and the queue has been deleted
            # FIXME: catches way too much, we need to somehow tell the thread to stop when the TaskManager gets deleted
            log.warning('TaskManager: task failed with type error: %s' % e)
            raise
            pass
        except Exception, e:
            log.warning('TaskManager: task failed unexpectedly with error: %s' % e)
        finally:
            queue.task_done()


# FIXME: switch me to PriorityQueue when we have python2.6
class TaskManager(Queue, object):
    """The TaskManager is a stable priority queue of tasks. It takes them one by one, the
    one with the highest priority first, and call its perform() method, then repeat until no tasks are left.

    If two or more tasks have the same priority, it will take the one that was added first to the queue.

    The TaskManager can be controlled asynchronously, as it runs the tasks in a separate thread."""

    def __init__(self, progressCallback = None):
        super(TaskManager, self).__init__()

        self.progressCallback = progressCallback

        self.total = 0
        self.totalLock = Lock()

        t = Thread(target = worker, args = (self,))
        # FIXME: for python2.6
        #t.daemon = True
        t.setDaemon(True)
        t.start()

    def add(self, task):
        # -task.priority because it always gets the lowest one first
        # we need to put the time as well, because Queue uses heap sort which is not stable, so we
        # had to find a way to make it look stable ;-)
        with self.totalLock:
            self.total += 1
            self.put(( (-task.priority, time.time()), task ))


    def task_done(self):
        log.info('Task completed!')
        with self.totalLock:
            # if we finished all the tasks, reset the current total
            if self.empty():
                self.total = 0

            if self.progressCallback:
                self.progressCallback(self.total - self.qsize(), self.total)

        super(TaskManager, self).task_done()
