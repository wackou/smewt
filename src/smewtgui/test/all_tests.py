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

import sys
import unittest
import glob


def importTest(name):
    cmd = 'import test_%s; setattr(sys.modules[__name__], \'%s\', test_%s.suite)' % (name, name, name)
    exec(cmd)


listTests = [ filename[5:-3] for filename in glob.glob('test_*.py') ]

for test in listTests:
    importTest(test)

testObjectsList = [ getattr(sys.modules[__name__], name) for name in listTests ]

all = unittest.TestSuite(testObjectsList)

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(all)
