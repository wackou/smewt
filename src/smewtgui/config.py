#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack
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


'''Main config file

This file contains various configuration options that define which version of
the program to use.

This is not to be mistaken with the program settings, which contains the user
preferences.
'''

# whether to connect to Smewtd
connect_smewtd = False


# whether to retrieve locally stored results for web queries
test_localweb = False

local_epguides_googleresult = 'testdata/allintitle: site:epguides.com futurama - Google Search.html'
local_epguides_episodelist = 'testdata/Futurama (a Titles & Air Dates Guide).html'