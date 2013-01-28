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

# NOTE: the following has been shamelessly taken from this URL:
# http://www.willmcgugan.com/blog/tech/2012/12/9/where-are-those-print-statements/

import inspect
import sys
import os


class DebugPrint(object):
    def __init__(self, f):
        self.f = f

    def write(self, text):
        frame = inspect.currentframe()
        filename = frame.f_back.f_code.co_filename.rsplit(os.sep, 1)[-1]
        lineno = frame.f_back.f_lineno
        prefix = "[%s:%s] " % (filename, lineno)
        if text == os.linesep:
            self.f.write(text)
        else:
            self.f.write(prefix + text)

if not isinstance(sys.stdout, DebugPrint):
    sys.stdout = DebugPrint(sys.stdout)
