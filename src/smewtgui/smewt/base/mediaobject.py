#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Ricard Marxer <email@ricardmarxer.com>
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

from smewtdict import SmewtDict, ValidatingSmewtDict
from smewtexception import SmewtException

# This file contains the 2 base MediaObject types used in Smewt:
#  - Media: is the type used to represent physical files on the hard disk.
#    It always has at least 2 properties: 'filename' and 'sha1'
#  - Metadata: is the type used to represent a media entity independent
#    of its physical location.
#
# Two MediaObject can point to the same AbstractMediaObject, such as the video and
# the subtitle files for an episode will point to the same Episode AbstractMediaObject
#
# The job of a guesser is to map a MediaObject to its corresponding AbstractMediaObject


class Media(object):

    typename = 'Media' # useful for printing sometimes when mixed with Metadata objs

    types = { 'video': [ 'avi', 'ogm', 'mkv', 'mpg', 'mpeg' ],
              'subtitle': [ 'sub', 'srt' ]
              }

    def __init__(self, filename = ''):
        self.filename = unicode(filename)
        self.sha1 = ''
        self.metadata = None # ref to a Metadata object

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return self.filename.encode('utf-8')

    def __eq__(self, other):
        # FIXME: why do we need that try/except?
        try:
            return isinstance(other, Media) and self.filename == other.filename
        except AttributeError:
            return hash(None)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # should be sha1 when we have it
        # FIXME: why do we need that try/except?
        try:
            return hash(self.filename)
        except AttributeError:
            return hash(None)

    def type(self):
        for name, exts in Media.types.items():
            for ext in exts:
                if self.filename.endswith(ext):
                    return name
        return 'unknown type'

    def uniqueKey(self):
        return self.filename




# TODO: isn't it better to implement properties as actual python properties? or attributes?
# TODO: !!write unit tests for this class...!!
class Metadata(object):
    ''' This is the class which all the metadata objects should inherit.
    We assume the implementation of the Metadata objects come from plugins.

    The following needs to be defined in derived classes:

    1- 'typename' which is a string representing the type name

    2- 'schema' which is a dictionary from property name to type
    ex: schema = { 'epNumber': int,
                   'title': str
                   }

    3- 'converters', which is a dictionary from property name to
       a function that is able to parse this property from a string

    4- 'unique' which is the list of properties that form a primary key
    '''

    def __init__(self, copy = None, dictionary = {}, headers = [], row = []):
        # create the properties
        self.properties = ValidatingSmewtDict(self.schema)
        self.confidence = None

        # self.mutable should be set to False whenever the object needs to be hashable, such as when
        # we want to put it in a set or a Graph. When self.mutable is False, none of the properties which
        # are in its self.unique list can be changed anymore, although the other ones still can.
        self.mutable = True

        #for prop in self.schema:
        #    self.properties[prop] = None

        if copy:
            if isinstance(copy, dict):
                self.readFromDict(copy)
            else:
                self.readFromDict(copy.toDict())
            return

        if dictionary:
            self.readFromDict(dictionary)
            return

        if headers and row:
            self.readFromRow(headers, row)
            return

    def __getstate__(self):
        return self.toDict(), self.confidence

    def __setstate__(self, state):
        self.__init__(state[0])
        self.confidence = state[1]


    # used to make sure the values correspond to the schema
    def isValid(self):
        # compare properties' type
        try:
            for prop in self.schema.keys():
                if self.properties[prop] is not None and type(self.properties[prop]) != self.schema[prop]:
                    return False
        except KeyError:
            return False

        return True

    def isUnique(self):
        for prop in self.unique:
            if self.properties[prop] is None:
                return False
        return True


    def __repr__(self):
        return str(self)

    def __str__(self):
        result = ('valid ' if self.isValid() else 'invalid ') + self.typename + ' (confidence: ' + str(self.confidence) + ') :\n{ '

        for propname in self.orderedProperties():
            result += '%-10s : %s\n  ' % (propname, unicode(self.properties[propname]).encode('utf-8'))

        return result + '}'


    def orderedProperties(self):
        '''Returns the list of properties ordered using the defined order in the subclass'''
        result = []
        propertyNames = self.properties.keys()

        try:
            for p in self.order:
                if p in propertyNames:
                    result += [ p ]
                    propertyNames.remove(p)
        except AttributeError:
            return propertyNames

        return result + propertyNames

    def keys(self):
        return self.properties.keys()

    def items(self):
        return self.properties.items()

    def getAttributes(self, attrs):
        result = [ self[attr] for attr in attrs ]
        return tuple(result)

    def uniqueKey(self):
        return self.getAttributes(self.unique)

    def __eq__(self, other):
        if other is None or type(self) != type(other):
            return False
        return self.uniqueKey() == other.uniqueKey()

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.__class__, self.uniqueKey()))

    def __getitem__(self, prop):
        return self.properties[prop]

    def __setitem__(self, prop, value):
        if not self.mutable and prop in self.unique:
            raise SmewtException("Metadata: cannot change property '%s' because object '%s' is immutable" % (prop, self))
        self.properties[prop] = self.parse(self, prop, value)

    def merge(self, other):
        for name, prop in other.properties.items():
            self.properties[name] = prop

    def mergeNew(self, other):
        for name, value in other.properties.items():
            if name not in self.properties:
                self.properties[name] = value


    def setdefault(self, prop, value):
        if not prop in self.properties:
            self.properties[prop] = value

        return self.properties[prop]

    def contains(self, other):
        for name, prop in other.properties.items():
            if self.properties[name] != prop:
                return False
        return True

    @staticmethod
    def parse(cls, name, value):
        if name not in cls.schema:
            return value

        elif isinstance(value, cls.schema[name]):
            # if we have a preexisting smewt object of the correct type (ie: no literal), use the ref to it
            return value

        elif name in cls.converters:
            # types that need a specific conversion
            return cls.converters[name](value)

        else:
            # otherwise just call the default constructor
            return cls.schema[name](value)

    def parseProperty(self, name, value):
        return self.parse(self, name, value)

    def toDict(self):
        return dict(self.properties)


    def readFromDict(self, d):
        for prop, value in d.items():
            self.properties[prop] = self.parseProperty(prop, value)

    def fromDict(self, d):
        self.readFromDict(d)
        return self

    def readFromRow(self, headers, row):
        '''giving too much information in the row is not a problem,
        extra fields will be ignored'''
        # OR
        '''if a key from the headers is not in the schema, error because
        the user could have misspelt it'''
        # ?

        for prop, value in zip(headers, row):
            try:
                self.properties[prop] = self.parseProperty(prop, value)

            except KeyError:
                # property name is not in the schema
                pass

    def fromRow(self, headers, row):
        self.readFromRow(headers, row)
        return self
