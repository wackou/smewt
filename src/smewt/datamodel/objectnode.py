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
from basicgraph import BasicNode
from utils import tolist, toresult, isOf
import ontology
import types
import logging

log = logging.getLogger('smewt.datamodel.ObjectNode')



class ObjectNode(BasicNode):
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

    def __init__(self, graph, props = []):
        print 'ObjectNode.__init__'
        super(ObjectNode, self).__init__(graph, props)

        print 'setting', props
        for prop, value, reverseName in props:
            self.set(prop, value, reverseName, validate = False)

        print 'update valid classes'
        self.updateValidClasses()


    def isValidInstance(self, cls):
        # if graphType == 'DYNAMIC': return True # != 'STATIC'
        for prop in cls.valid:
            value = self.get(prop)

            if isinstance(value, types.GeneratorType):
                value = list(value)
                if value != [] and not value[0].isinstance(cls.schema[prop]):
                    return False
            # TODO: remove this elif
            elif isinstance(value, BasicNode):
                # TODO: we might need value.isValidInstance in some cases
                if not value.isinstance(cls.schema[prop]):
                    return False
            else:
                # TODO: here we might want to check if value is None and allow it or not
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
        self.clearClasses()
        for cls in ontology._classes.values():
            if self.isValidInstance(cls):
                self.addClass(cls)
        #self._classes = set([ cls for cls in ontology._classes.values() if self.isValidInstance(cls) ])

        log.debug('valid classes for %s:\n  %s' % (self.toString(), [ cls.__name__ for cls in self._classes ]))


    ### Container methods

    def keys(self):
        for k in self.literalKeys():
            yield k
        for k in self.edgeKeys():
            yield k

    def values(self):
        for v in self.literalValues():
            yield v
        for v in self.edgeValues():
            yield v

    def items(self):
        for i in self.literalItems():
            yield i
        for i in self.edgeItems():
            yield i

    def __iter__(self):
        for prop in self.keys():
            yield prop

    def __getattr__(self, name):
        return self.get(name)

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        # TODO: why do we need this again?
        raise NotImplementedError


    ### Acessing properties methods

    def get(self, name):
        """Returns the given property or None if not found.
        This can return either a literal value, or an iterator through other nodes if
        the given property actually was a link relation."""
        try:
            return self.getLiteral(name)
        except:
            try:
                return self.getLink(name) # TODO: this should return an iterator to the pointed nodes
            except:
                return None


    ### properties manipulation methods

    def __setattr__(self, name, value):
        if name in [ '_graph', '_classes' ]:
            object.__setattr__(self, name, value)
        else:
            self.set(name, value)

    def set(self, name, value, reverseName = None, validate = True):
        """Sets the property name to the given value.

        If value is an ObjectNode, we're actually setting a link between them two, so we use reverseName as the
        name of the link when followed in the other direction.
        If reverseName is not given, a default of 'isNameOf' (using the given name) will be used."""

        if isinstance(value, ObjectNode):
            if reverseName is None:
                #raise ValueError('When setting a link between 2 nodes, you also need to give a reverseName for the link.')
                reverseName = isOf(name)

            self.setLink(name, value, reverseName)

        elif type(value) in ontology.validLiteralTypes or value is None:
            self.setLiteral(name, value)

        else:
            raise TypeError("Trying to set property '%s' of %s to '%s', but it is not of a supported type (literal or object node): %s" % (name, self, value, type(value).__name__))

        # update the cache of valid classes
        if validate:
            self.updateValidClasses()

    def setLink(self, name, otherNode, reverseName):
        """Can assume that value is always an object node."""
        # TODO: remove check later
        if not isinstance(otherNode, ObjectNode):
            raise TypeError('otherNode should be an ObjectNode, but is it a %s' % type(otherNode).__name__)

        if self._graph != otherNode._graph:
            raise ValueError('Both nodes do not live in the same graph, cannot link them together')

        g = self._graph

        # first remove the old link(s)
        for n in tolist(self.get(name)):
            g.removeLink(self, name, n, reverseName)

        # then add the new link
        g.addLink(self, name, otherNode, reverseName)



    def update(self, props):
        """Update this ObjectNode properties with the ones contained in the given dict.
        Should also allow instances of other ObjectNodes."""
        for name, value in props.items():
            self.set(name, value, validate = False)

        self.updateValidClasses()

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
