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
from objectnode import ObjectNode
from baseobject import BaseObject #, getNode
import logging

log = logging.getLogger('smewt.datamodel.MemoryObjectNode')

class MemoryObjectNode(ObjectNode):

    def __init__(self, graph, props = []):
        # NB: this should go before super().__init__() because we need self._props to exist
        #     before we can set attributes
        self._props = {}
        ObjectNode.__init__(self, graph, props)

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        # TODO: verify me
        return id(self)

    ### Acessing properties methods

    def __getattr__(self, name):
        # FIXME: THIS METHOD IS OUTDATED

        # TODO: this should go into the PersistentObjectNode
        #if name == '_node':
        #    return self.__dict__[name]

        try:
            result = self._props[name]
            #if isinstance(result, BaseObject):
            #    result = result._node

            return result
        except KeyError:
            # if attribute was not found, look whether it might be a reverse attribute
            if name.startswith('is_') and name.endswith('_of'):
                if self._graph is None:
                    raise AttributeError, 'Cannot get reverse attribute of node for which no Graph has been set'
                return self._graph.reverseLookup(self, name[3:-3])

            # TODO: find valid classes which have a method with a corresponding name
            classes = [ c for c in self._classes if name in c.__dict__ ]


            raise AttributeError, name


    def __setattr__(self, name, value):
        if name == '_props':
            object.__setattr__(self, name, value)
        else:
            ObjectNode.__setattr__(self, name, value)


    def setLiteral(self, name, value):
        self._props[name] = value


    ### Container methods

    def keys(self):
        return self._props.keys()

    def values(self):
        return self._props.values()

    def items(self):
        return self._props.items()


    ### manipulation methods

    def updateNew(self, other):
        for name, value in other._props.items():
            if name not in self._props:
                self._props[name] = value

