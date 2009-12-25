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

class BaseObject(object):
    """Derive from this class to define an ontology domain.

    Instantiating an object through derived classes should return an ObjectNode and
    not a derived class instance.

    You should define the following class variables in derived classes:

    1- 'schema' which is a map of property names to their respective types
    ex: schema = { 'epNumber': int,
                   'title': str
                   }

    2- 'unique' which is the list of properties that form a primary key

    3- 'order' (optional) which is a list of properties you always want to see in front for debug msgs

    4- 'converters' (optional), which is a dictionary from property name to
       a pair of functions that are able to serialize/deserialize this property to/from a unicode string.


    NB: this class only has class methods, because as instantiated objects are ObjectNodes instances,
    we could not even call member functions from this subclass.
    """

    order = []
    converters = {}

    @classmethod
    def className(cls):
        return cls.__name__

    @classmethod
    def parentClass(cls):
        return cls.__mro__[1]

    def __new__(cls, **kwargs):
        return ObjectNode(cls, **kwargs)


class OntologyManager:

    _classes = { 'BaseObject': BaseObject }

    @staticmethod
    def register(*args):
        # can only register classes which are subclasses of our BaseObject class.
        for cls in args:
            if not issubclass(cls, BaseObject):
                raise TypeError, '%s needs to derive from ontology.BaseObject' % cls.__name__

            # TODO: validate our subclass (does it have a correct schema defined, etc...)
            try:
                if not isinstance(cls.schema, dict) or not isinstance(cls.unique, list):
                    raise TypeError
            except:
                raise TypeError, "Your subclass '%s' should define at least the 'schema' class variable as a dict and the 'unique' one as a list" % cls.__name__

            OntologyManager._classes[cls.__name__] = cls


    @staticmethod
    def getClass(className):
        """Returns the ObjectNode class object given its name."""
        try:
            return OntologyManager._classes[className]
        except:
            raise ValueError, 'Class "%s" has not been registered with the OntologyManager' % className
