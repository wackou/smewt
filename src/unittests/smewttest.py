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

import yaml, logging, sys, os
from os.path import *

def currentPath():
    '''Returns the path in which the calling file is located.'''
    return dirname(join(os.getcwd(), sys._getframe(1).f_globals['__file__']))

def addImportPath(path):
    '''Function that adds the specified path to the import path. The path can be
    absolute or relative to the calling file.'''
    importPath = abspath(join(currentPath(), path))
    sys.path = [ importPath ] + sys.path

addImportPath('.')  # for the tests
addImportPath('..') # for import smewt

from smewt import *
from smewt.datamodel import *
from smewt.solvers import *
from smewt.guessers import *
from smewt.media import *

# before starting any tests, save smewt's default ontology in case we mess with it and need it again later
ontology.saveCurrentOntology('media')

def allTests(testClass):
    return TestLoader().loadTestsFromTestCase(testClass)
