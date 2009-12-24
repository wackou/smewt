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

class BaseClass(object):
    """Derive from this class to define an ontology domain.

    Instantiating an object through derived classes should return an ObjectNode and
    not DerivedClass instance.

    You should define the following in derived classes:

    1- 'typename' which is a string representing the type name
       ## Not anymore, should be registered and taken as the basename of the subclass

    2- 'schema' which is a dictionary from property name to type
    ex: schema = { 'epNumber': int,
                   'title': str
                   }
      ## probably could define them as class attributes, the way django does it

    3- 'converters', which is a dictionary from property name to
       a pair of functions that are able to serialize/deserialize this property to/from a unicode string.

    4- 'unique' which is the list of properties that form a primary key

    this class only has static methods, because as instantiated object are ObjectNodes, we
    could not even call member functions from this subclass.
    """

    @staticmethod
    def className(cls):
        return cls.__name__

    @staticmethod
    def parentClass(cls):
        return cls.__mro__[1]

    @staticmethod
    def issubclass(cls, base):
        # WARNING: this is not correct with multiple inheritance
        while cls != base and cls != BaseClass:
            cls = BaseClass.parentClass(cls)
        return cls == base


class OntologyManager:

    _classes = { 'BaseClass': BaseClass }

    @staticmethod
    def register(*args):
        # can only register classes which are subclasses of our BaseClass class.
        for cls in args:
            if not issubclass(cls, BaseClass):
                raise ValueError, '%s needs to derive from ontology.BaseClass' %

            # TODO: validate our subclass (does it have a correct schema defined, etc...)

            _classes[cls.__name__] = cls


    @staticmethod
    def getClass(className):
        """Returns the ObjectNode class object given its name."""
        pass

    @staticmethod
    def issubclass(cls, base):
        pass
