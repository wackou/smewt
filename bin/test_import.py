#!/usr/bin/env python
# -*- coding: utf-8 -*-

# README
#
# run with:
#   python -m cProfile -o /tmp/profstats bin/test_import.py
# view with
#   runsnake /tmp/profstats

from PyQt4.QtGui import QApplication
from smewt.base.smewtdaemon import SmewtDaemon
from guessit import slogging
import sys
import smewt
import logging

slogging.setupLogging()
logging.getLogger().setLevel(logging.INFO)
log = logging.getLogger(__name__)



app = QApplication(sys.argv)
app.setOrganizationName(smewt.ORG_NAME)
app.setOrganizationDomain('smewt.com')
app.setApplicationName(smewt.APP_NAME)


s = SmewtDaemon()
print len(list(s.database.nodes()))

print 'NUM TASKS IN Q:', s.taskManager.queue.qsize()

#s.updateCollections()
s.rescanCollections()
s.taskManager.finishNow()

# do the rest on the main thread to be able to profile it efficiently
q = s.taskManager.queue

while q.qsize() > 0:
    print 'NUM TASKS IN Q:', q.qsize()
    (_, _), task = q.get()
    task.perform()
