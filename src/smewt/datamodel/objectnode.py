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

import logging

log = logging.getLogger('smewt.datamodel.ObjectNode')

class ObjectNode:
    """An ObjectNode is a nice and useful mix between an OOP object and a node in a graph.

    An ObjectNode behaves in the following way:
     - it can have any number of named properties, of any type (literal type or another ObjectNode)
     - it implements dotted attribute access.
     - it still has a class which "declares" a schema of standard properties and their types, like a normal object in OOP
     - it can be validated against that schema (ie: do the actual properties have the same type as those declared in the class definition)
     - setting attributes can be validated for type in real-time
     - it has primary properties, which are used as primary key for identifying ObjectNodes or for indexing

    ObjectNodes should implement different types of equalities:
      - all their properties are equal (same type and values)
      - all their standard properties are equal
      - only their primary properties are equal

    To be precise, ObjectNodes use a type system based on relaxed type classes
    (http://en.wikipedia.org/wiki/Type_classes)
    where there is a standard object hierarchy, but an ObjectNode can be of various distinct
    classes at the same time.

    As this doesn't fit exactly with python's way of doing things, class value should be tested
    using the ObjectNode.isinstance(class) and ObjectNode.issubclass(class, subclass) methods,
    instead of the usual isinstance(obj, class) function.

    Classes which have been registered in the global ontology can also be tested with their basename
    given as a string (ie: node.isinstance('Movie'))
    """
    pass
