#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2012 Nicolas Wack <wackou@smewt.com>
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

from PyQt4.QtGui import *
from PyQt4.QtCore import QObject, SIGNAL, QSettings
import smewt
import guessit
from smewt.base.utils import smewtDirectory
from smewt.base import cache


def guiLanguage():
    language = str(QSettings().value('gui/language', 'en').toString())
    return guessit.Language(language)


class SettingsDialog(QDialog):
    def __init__(self, *args):
        QDialog.__init__(self, *args)

        self.setWindowTitle('Settings')
        self.resize(400, 450)

        self.layout = QVBoxLayout()


        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('GUI Language:'))
        self.lang_edit = QLineEdit(guiLanguage().alpha2)
        hlayout.addWidget(self.lang_edit)
        self.layout.addLayout(hlayout)

        hlayout = QHBoxLayout()
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Cancel')
        hlayout.addWidget(self.ok_button)
        hlayout.addWidget(self.cancel_button)

        self.layout.addLayout(hlayout)

        self.setLayout(self.layout)

        self.connect(self.ok_button, SIGNAL('clicked()'),
                     self.saveSettings)

        self.connect(self.cancel_button, SIGNAL('clicked()'),
                     self.reject)


    def saveSettings(self):
        QSettings().setValue('gui/language', guessit.Language(str(self.lang_edit.text())).lang)
        cache.clear()
        self.accept()
