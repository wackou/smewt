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

from PyQt4.QtGui import *
from PyQt4.QtCore import QObject, SIGNAL
import smewt
from smewt.base.utils import smewtDirectory

class AboutDialog(QDialog):
    def __init__(self, *args):
        QDialog.__init__(self, *args)

        self.setWindowTitle('About Smewt')
        self.resize(400, 450)

        layout = QVBoxLayout()

        header = QFrame()
        header.setFrameShape(QFrame.StyledPanel)
        header.setFrameShadow(QFrame.Sunken)
        headerLayout = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(QPixmap(smewtDirectory('smewt', 'icons', 'smewt_64x64.png')))
        headerLayout.addWidget(icon)
        headerLayout.addWidget(QLabel('<h2>Smewt</h2><p><b>Version:</b> %s</p>' % smewt.__version__))
        headerLayout.addStretch()
        header.setLayout(headerLayout)

        tabs = QTabWidget()

        aboutTab = QTextBrowser()
        aboutTab.setFrameShape(QFrame.NoFrame)
        aboutTab.setStyleSheet('QTextBrowser { background:transparent }')
        aboutTab.setOpenExternalLinks(True)
        aboutTab.setHtml('<p><b>A Smart media manager</b></p>'
                         ''
                         '<p>&copy;2008-2011 by the Smewt developers<br/>'
                         '<a href="http://www.smewt.com">http://www.smewt.com</a><br/>'
                         '<a href="irc://irc.freenode.net/smewt">#smewt</a> on <a href="http://freenode.net">Freenode</a></p>'
                         ''
                         '<p>Smewt is licensed under the <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p>'
                         '<p>Please use <a href="http://code.google.com/p/smewt/">http://code.google.com/p/smewt/</a> to report bugs.</p>')

        authorsTab = QTextBrowser()
        authorsTab.setFrameShape(QFrame.NoFrame)
        authorsTab.setStyleSheet('QTextBrowser { background:transparent }')
        authorsTab.setOpenExternalLinks(True)
        authorsTab.setHtml('Smewt is developed by:'
                           '<dl>'
                           '<dt><b>Nicolas Wack</b></dt>'
                           '<dd><a href="mailto:wackou@gmail.com">wackou@gmail.com</a><br/>'
                           'Project Founder, Lead Developer</dd>'
                           '<dt><b>Ricard Marxer</b></dt>'
                           '<dd><a href="mailto:email@ricardmarxer.com">email@ricardmarxer.com</a><br/>'
                           'Lead Developer</dd>'
                           '</dl>')
                           

        thanksTab = QTextBrowser()
        thanksTab.setFrameShape(QFrame.NoFrame)
        thanksTab.setStyleSheet('QTextBrowser { background:transparent }')
        thanksTab.setOpenExternalLinks(True)
        thanksTab.setHtml('Special thanks go to:<br/>'
                          '<dl>'
                          '<dt><b><a href=\"http://www.oxygen-icons.org\">The Oxygen Team</a></b></dt>'
                          '<dd>for most of the icons in Smewt and on the website</dd>'
                          '<dt><b><a href="http://www.openclipart.org/user-detail/papapishu">Papapishu</a></b></dt>'
                          '<dd>for the <a href="http://www.openclipart.org/detail/23677">Fried egg</a> icon</dd>'
                          '<dt><b><a href="http://famfamfam.com/">Mark James</a></b></dt>'
                          '<dd>for the <a href="http://famfamfam.com/lab/icons/flags/">flag icons</a></dd>'
                          '<dt><b><a href="http://www.davehylands.com/">Dave Hylands</a></b></dt>'
                          '<dd>for the <a href="http://www.davehylands.com/Software/Open/">open.exe</a> utility on Windows</dd>')
                          

        tabs.addTab(aboutTab, 'About')
        tabs.addTab(authorsTab, 'Authors')
        tabs.addTab(thanksTab, 'Thanks to')

        closeLayout = QHBoxLayout()
        closeLayout.addStretch()
        closeButton = QPushButton('Close')
        QObject.connect(closeButton, SIGNAL('clicked()'), self.accept)
        closeLayout.addWidget(closeButton)


        layout.addWidget(header)
        layout.addWidget(tabs)
        layout.addLayout(closeLayout)

        self.setLayout(layout)
        
