#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2009 Nicolas Wack <wackou@gmail.com>
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

from objectnode import ObjectNode
import logging

log = logging.getLogger('smewt.datamodel.Ontology')

class BaseClass:
    """Derive from this class to define an ontology domain.

    Instantiating an object through derived classes should return an ObjectNode and
    not DerivedClass instance.

    you should define the following in derived classes:
    """

class OntologyManager:

    @staticmethod
    def register(*args):
        for cls in args:
            if not issubclass(cls, BaseClass):
                raise ValueError, 'need to derive from ontology.BaseClass'
        # TODO: register the name in a map
        pass

