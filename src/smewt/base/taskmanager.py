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

from PyQt4.QtCore import SIGNAL, Qt, QObject, QThread

class Task:
    def __init__(self):
        pass

    def perform(taskData):
        """All tasks should implement this function, which should perform the actual task.

        Data is passed to this method using the opaque 'taskData' variable, its type and contents depending
        on the type of task being performed.

        This method shouldn't return anything on success, and raise an exception in case of failure.
        It can have side effects, such as updating the global collection, though. In this case, the
        collection needs to be passed through the 'taskData' input variable."""
        raise NotImplementedError


'''
class Task:
    def __init__(self):
        self.name = 'Unnamed task'
        self.totalCount = 0
        self.progressedCount = 0

    def total(self):
        return self.totalCount

    def progressed(self):
        return self.progressedCount

    def abort(self):
        pass

    def update(self):
        pass
'''


class TaskManager(QObject, Task):
    def __init__(self):
        super(TaskManager, self).__init__()

        self.tasks = []
        self.totalCount = 0
        self.progressedCount = 0

    def add(self, task):
        self.tasks.append( task )
        self.connect(task, SIGNAL('progressChanged'), self.progressChanged)
        self.connect(task, SIGNAL('taskFinished'), self.taskFinished)
        self.progressChanged()

    def remove(self, task):
        assert task in self.tasks, "The task is not registered to the task manager."

        self.tasks.remove( task )

        del task
        self.progressChanged()

    def update(self):
        # Get the total and progressed of the task
        self.totalCount = 0
        self.progressedCount = 0
        for task in self.tasks:
            task.update()
            self.totalCount += task.total()
            self.progressedCount += task.progressed()

    def taskFinished(self, task):
        self.progressChanged()

    def progressChanged(self):
        self.update()
        self.emit(SIGNAL('progressChanged'), self.progressed(), self.total())

    def abortAll(self):
        for task in self.tasks:
            task.abort()

    def total(self):
        return self.totalCount

    def progressed(self):
        return self.progressedCount
