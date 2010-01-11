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

from smewt.base.textutils import toUtf8
import ontology
import logging

log = logging.getLogger('smewt.datamodel.ObjectNode')

class ObjectNode(object):
    """An ObjectNode is a nice and useful mix between an OOP object and a node in a graph.

    An ObjectNode behaves in the following way:
     - it can have any number of named properties, of any type (literal type or another ObjectNode)
     - it implements dotted attribute access.
     - DEPRECATED(*): it still has a class which "declares" a schema of standard properties and their types, like a normal object in OOP
     - DEPRECATED(*): it can be validated against that schema (ie: do the actual properties have the same type as those declared in the class definition)
     - DEPRECATED(*): setting attributes can be validated for type in real-time
     - DEPRECATED(*): it has primary properties, which are used as primary key for identifying ObjectNodes or for indexing purposes

    ObjectNodes should implement different types of equalities:
      - identity: both refs point to the same node in the ObjectGraph
      - all their properties are equal (same type and values)
      - DEPRECATED(*) all their standard properties are equal
      - DEPRECATED(*) only their primary properties are equal

    (*) this should now be done in BaseObject instances instead of directly on the ObjectNode.

    ---------------------------------------------------------------------------------------------------------

    To be precise, ObjectNodes use a type system based on relaxed type classes
    (http://en.wikipedia.org/wiki/Type_classes)
    where there is a standard object hierarchy, but an ObjectNode can be of various distinct
    classes at the same time.

    As this doesn't fit exactly with python's way of doing things, class value should be tested
    using the ObjectNode.isinstance(class) and ObjectNode.issubclass(class, subclass) methods,
    instead of the usual isinstance(obj, class) function.

    Classes which have been registered in the global ontology can also be tested with their basename
    given as a string (ie: node.isinstance('Movie')) to avoid too many importing headaches.

    ---------------------------------------------------------------------------------------------------------

    Accessing properties should return a "smart" iterator when accessing properties which are instances of
    BaseObject, which also allows to call dotted attribute access on it, so that this becomes possible:

    for f in Series.episodes.file.filename:
        do_sth()

    where Series.episodes returns multiple results, but Episode.file might also return multiple results.
    File.filename returns a literal property, which means that we can now convert our iterator over BaseObject
    into a list (or single element) of literal
    """

    def __init__(self, graph):
        self._graph = graph
        self.updateValidClasses()

    def isValidInstance(self, cls):
        for prop in cls.valid:
            if prop not in self:
                return False

            if True: # graphType == 'STATIC'
                value = getattr(self, prop)

                if isinstance(value, ObjectNode):
                    # TODO: check isValidInstance
                    if not value.isValidInstance(cls.schema[prop]):
                        return False
                else:
                    if type(value) != cls.schema[prop]:
                        return False

        return True


    def invalidProperties(self, cls):
        invalid = []
        for prop in cls.valid:
            if prop not in self:
                invalid.append("property '%s' is missing" % prop)
                continue

            if type(getattr(self, prop)) != cls.schema[prop]:
                invalid.append("property '%s' is of type '%s', but should be of type '%s'" %
                               (prop, type(getattr(self, prop)).__name__, cls.schema[prop].__name__))

        return '\n'.join(invalid)


    def updateValidClasses(self):
        self._classes = [ cls for cls in ontology._classes.values() if self.isValidInstance(cls) ]

        log.debug('valid classes for %s:\n  %s' % (self.toString(), self._classes))


    def isinstance(self, cls):
        # this should deal with inheritance correctly, as if this node is a correct instance
        # of a derived class, it should also necessarily be a correct instance of a parent class
        # TODO: for this to be true, we must make sure that derived classes in the ontology
        #       do not override properties defined in a parent class
        if cls in self._classes:
            return True

        # maybe we changed some value that now made this into a valid class, just revalidate
        # to make sure
        # TODO: this should probably go into setattr to revalidate in realtime (only for
        #       arguments which are not part of the schema, for optimization)
        self.updateValidClasses()

        return cls in self._classes


    def __eq__(self, other):
        # This should implement identity of nodes, not properties equality (this should be done
        # in the BaseObject instance)
        raise NotImplementedError


    def sameProperties(self, other, exclude = []):
        # NB: sameValidProperties and sameUniqueProperties should be defined in BaseObject
        # TODO: this can surely be optimized
        try:
            for name, value in sorted(other.items()):
                if name in exclude:
                    continue
                if getattr(self, name) != value:
                    return False

            return True

        except AttributeError:
            return False

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # TODO: why do we need this again?
        raise NotImplementedError


    ### Acessing properties methods

    def get(self, name):
        """Returns the given property or None if not found."""
        try:
            return getattr(self, name)
        except AttributeError:
            return None

    def __getattr__(self, name):
        raise NotImplementedError

    def __setattr__(self, name, value):
        if name in [ '_graph', '_classes' ]:
            object.__setattr__(self, name, value)
        else:
            self.set(name, value)

    def set(self, name, value, reverseName = None):
        """Sets the property name to the given value.

        If value is an ObjectNode, we're actually setting a link between them two, so we use reverseName as the
        name of the link when followed in the other direction.
        If reverseName is not given, a default of 'isNameOf' (using the given name) will be used."""

        if isinstance(value, ObjectNode):
            self.setLink(name, value, reverseName)
        elif type(value) in ontology.validLiteralTypes or value is None:
            self.setLiteral(name, value)
        else:
            raise TypeError("Trying to set property '%s' of %s to '%s', but it is not of a supported type (literal or object node): %s" % (name, self, value, type(value).__name__))


    def setLiteral(self, name, value):
        """Need to be implemented by implementation subclass.
        Can assume that literal is always one of the valid literal types."""
        raise NotImplementedError

    def setLink(self, name, value, reverseName = None):
        """Can assume that value is always an object node."""
        if self._graph != value._graph:
            raise ValueError('Both nodes do not live in the same graph, cannot link them together')

        if reverseName is None:
            reverseName = 'is%sOf' % (name[0].upper() + name[1:])

        self._graph.setLink(self, name, value, reverseName)


    ### Container methods

    def keys(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def values(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def items(self):
        # TODO: should return an iterator
        raise NotImplementedError

    def __iter__(self):
        for prop in self.keys():
            yield prop


    ### properties manipulation methods

    def update(self, props):
        """Update this ObjectNode properties with the ones contained in the given dict.
        Should also allow instances of other ObjectNode, or even BaseObject."""
        for name, value in props.items():
            setattr(self, name, value)

    def updateNew(self, other):
        """Update this ObjectNode properties with the only other ones it doesn't have yet."""
        raise NotImplementedError


    ### String methods

    def __str__(self):
        return self.toString().encode('utf-8')

    def __unicode__(self):
        return self.toString()

    def __repr__(self):
        return str(self)


    def toString(self, cls = None):
        if cls is None:
            # most likely called from a node, but anyway we can't infer anything on the links so just display
            # them as anonymous ObjectNodes
            cls = self.__class__
            props = [ (prop, cls.__name__) if isinstance(value, ObjectNode) else (prop, str(value)) for prop, value in self.items() ]

        else:
            props = [ (prop, value.toString(cls = cls.schema[prop]))                        # call toString with the inferred class of a node
                      if isinstance(value, ObjectNode) and prop in cls.schema               # if we have a node in our schema
                      else (prop, str(value))                                               # or just convert to string
                      for prop, value in self.items() if prop not in cls.schema._implicit ] # for all non-implicit properties

        return u'%s(%s)' % (cls.__name__, ', '.join([ u'%s=%s' % (k, v) for k, v in props ]))

    '''
    def toFullString(self, tabs = 0):
        tabstr = 4 * tabs * ' '
        tabstr1 = 4 * (tabs+1) * ' '
        result = ('valid ' if self.isValid() else 'invalid ') + self._class.__name__ + ' : {\n'

        schema = self._class.schema
        for propname in self.orderedProperties():
            if propname in schema and isinstance(self._props[propname], ObjectNode):
                s = self._props[propname].toString(tabs = tabs+1)
            else:
                s = toUtf8(self._props[propname])
            result += tabstr1 + '%-20s : %s\n' % (propname, s)

        return result + tabstr + '}'
    '''
