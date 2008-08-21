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

from smewt import SmewtDict,  ValidatingSmewtDict

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


class Media:

    types = { 'video': [ 'avi', 'ogm', 'mkv', 'mpg', 'mpeg' ]
              }

    def __init__(self, filename = ''):
        self.filename = unicode(filename)
        self.sha1 = ''
        self.metadata = None # ref to a Metadata object

    def type(self):
        for name, exts in Media.types.items():
            for ext in exts:
                if self.filename.endswith(ext):
                    return name
        return 'unknown type'



# TODO: isn't it better to implement properties as actual python properties? or attributes?
# TODO: !!write unit tests for this class...!!
class Metadata:
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

    def __init__(self, dictionary = {}, headers = [], row = []):
        # create the properties
        self.properties = ValidatingSmewtDict(self.schema)
        self.confidence = None

        #for prop in self.schema:
        #    self.properties[prop] = None

        if dictionary:
            self.readFromDict(dictionary)

        if headers and row:
            self.readFromRow(headers, row)


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
        #return self.typename + '(' + repr(self.properties) + ')'
        return str(self)

    # check this function still works correctly
    def __str__(self):
        result = ('valid ' if self.isValid() else 'invalid ') + self.typename + ' (confidence: ' + str(self.confidence) + ') :\n{ '
        for key, value in self.properties.items():
            result += '%-10s : %s\n  ' % (key, unicode(value))
        return result + '}'

    def keys(self):
        return self.properties.keys()

    def getAttributes(self, attrs):
        result = [ self[attr] for attr in attrs ]
        return tuple(result)

    def getUniqueKey(self):
        return self.getAttributes(self.unique)

    def __getitem__(self, prop):
        return self.properties[prop]

    def __setitem__(self, prop, value):
        #self.properties[prop] = value
        # automatic conversion, is that good?
        self.properties[prop] = self.parse(self, prop, value)

    @staticmethod
    def parse(cls, name, value):
        if name not in cls.schema:
            return value

        if name in cls.converters:
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

