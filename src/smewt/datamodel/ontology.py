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

    2- 'reverseLookup' are used to indicated the name to be used for
            # the property name when following a relationship between objects in the other direction
            # ie: if Episode(...).series == Series('Scrubs'), then we define automatically
            # a way to access the Episode() from the pointed to Series() object.
            # with 'series' -> 'episodes', we then have:
            # Series('Scrubs').episodes = [ Episode(...), Episode(...) ]
            # reverseLookup needs to be defined for each property which is a Node object

    3- 'valid' which is the list of properties a node needs to have to be able to be considered
               as a valid instance of this class

    4- 'unique' which is the list of properties that form a primary key

    5- 'order' (optional) which is a list of properties you always want to see in front for debug msgs

    6- 'converters' (optional), which is a dictionary from property name to
       a pair of functions that are able to serialize/deserialize this property to/from a unicode string.


    NB: this class only has class methods, because as instantiated objects are ObjectNodes instances,
    we could not even call member functions from this subclass.
    """
    # this should be set to the used ObjectNode class (ie: ObjectNode or PersistentObjectNode)
    _objectNodeClass = type(None)

    schema = {}
    reverseLookup = []
    order = []
    converters = {}

    def __init__(self, graph, basenode = None, **kwargs):
        if basenode is None:
            # MemoryObjectGraph._objectNodeImpl == MemoryObjectNode
            self._node = graph._objectNodeImpl(graph, **kwargs)
        else:
            # if basenode is already in this graph, no need to make a copy of it
            if basenode._graph is graph:
                self._node = basenode
            else:
                self._node = graph._objectNodeImpl(graph, **basenode.todict())
            self._node.update(kwargs)
        #if not isinstance(basenode, BaseObject) and not isinstance(basenode, BaseObject._objectNodeClass):
        #    raise TypeError("basenode should be an instance of BaseObject or %s" % _objectNodeClass.__name__)
        #self._node = basenode or ObjectNode(self.__class__, **kwargs)

    def isinstance(self, cls):
        if cls is BaseObject._objectNodeClass:
            return True
        return isinstance(self, cls)

    def __getattr__(self, name):
        return getattr(self._node, name)

    def __setattr__(self, name, value):
        if name == '_node':
            object.__setattr__(self, name, value)
        else:
            setattr(self._node, name, value)

    def __eq__(self, other):
        # TODO: should allow comparing a BaseObject with an ObjectNode
        if not isinstance(other, BaseObject): return False

        if self._node == other._node: return True
        # FIXME: this could lead to cycles or very long chained __eq__ calling on properties
        return self.items() == other.items()

    @classmethod
    def className(cls):
        return cls.__name__

    @classmethod
    def parentClass(cls):
        return cls.__mro__[1]

    '''
    def oops__new__(cls, **kwargs):
        print 'creating node'
        result = ObjectNode(cls, **kwargs)
        print 'node created'
        # we also need to call the intended constructor for the object, the one defined
        # in the class definition. It will not receive any other arguments than the fully
        # constructed ObjectNode
        cls.__init__(result)
        print 'node initialized'

        # BaseObject shouldn't need to be in the valid classes as it doesn't define
        # anything, and removing it here allows to avoid import dependency problems
        print 'RC', result._classes
        try: result._classes.remove(BaseObject)
        except ValueError: pass
        print 'RC', result._classes

        return result
    '''


def validateClassDefinition(cls):
    if not issubclass(cls, BaseObject):
        raise TypeError, "'%s' needs to derive from ontology.BaseObject" % cls.__name__

    # Note: voluntarily omit to put str as allowed types, unicode is much better
    #       and it will save us a *lot* of trouble
    # Note: list should only be list of literal values
    # TODO: add datetime
    validTypes = [ unicode, int, long, float, list, BaseObject ]

    def checkPresent(cls, var, ctype):
        try:
            value = getattr(cls, var)
        except AttributeError:
            raise TypeError("Your subclass '%s' should define the '%s' class variable as a '%s'" % (cls.__name__, var, ctype.__name__))
        if type(value) != ctype:
            raise TypeError("Your subclass '%s' defines the '%s' class variable as a '%s', but it should be of type '%s'" % (cls.__name__, var, type(value).__name__, ctype.__name__))

    def checkSchemaSubset(cls, var):
        checkPresent(cls, var, list)
        for prop in getattr(cls, var):
            if not prop in cls.schema:
                raise TypeError("In '%s': when defining '%s', you used the '%s' variable, which is not defined in the schema" % (cls.__name__, var, prop))

    # validate the schema is correctly defined
    checkPresent(cls, 'schema', dict)
    for name, ctype in cls.schema.items():
        if not isinstance(name, str) or not any(issubclass(ctype, dtype) for dtype in validTypes):
            raise TypeError("In '%s': the schema should be a dict of 'str' to either one of those accepted types (or a subclass of them): %s'" % (cls.__name__, ', '.join("'%s'" % c.__name__ for c in validTypes)))

    # all the properties defined as subclasses of BaseObject need to have an
    # associated reverseLookup entry
    checkPresent(cls, 'reverseLookup', list)
    objectProps = [ name for name, ctype in cls.schema.items() if issubclass(ctype, BaseObject) ]
    diff = set(cls.reverseLookup).symmetric_difference(set(objectProps))
    if diff:
        raise "In '%s': you should define exactly one reverseLookup name for each property in your schema that is a subclass of BaseObject, different ones: %s" % (cls.__name__, ', '.join("'%s'" % c for c in diff))

    checkSchemaSubset(cls, 'valid')
    checkSchemaSubset(cls, 'unique')
    checkSchemaSubset(cls, 'order')
    # TODO: validate converters


class OntologyManager:

    _classes = { 'BaseObject': BaseObject }

    @staticmethod
    def register(*args):
        # can only register classes which are subclasses of our BaseObject class.
        for cls in args:
            validateClassDefinition(cls)
            OntologyManager._classes[cls.__name__] = cls


    @staticmethod
    def getClass(className):
        """Returns the ObjectNode class object given its name."""
        try:
            return OntologyManager._classes[className]
        except:
            raise ValueError, 'Class "%s" has not been registered with the OntologyManager' % className
