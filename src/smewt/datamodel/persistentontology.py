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

from ontology import OntologyManager
import logging

log = logging.getLogger('smewt.datamodel.PersistentOntology')


class PersistentOntologyManager(OntologyManager):

    @staticmethod
    def register(*args):
        for cls in args:
            if not issubclass(cls, BaseClass):
                raise ValueError, 'need to derive from ontology.BaseClass'

        # TODO: register the classes in neo4j
        pass


    def getClassName(n):
        try:
            return list(n.relationships('class').outgoing)[0].end['name']
        except:
            return 'Node'


    def defineClass(className):
        db = smewtdb.neo
        cnode = db.node(name = className)
        db.reference_node.defineClass(cnode)
        #setClass(cnode, 'Class') # cannot have rel.start == rel.end
        return cnode

    def getClassNode(className):
        db = smewtdb.neo
        # TODO: should be cached
        for rel in db.reference_node.relationships('defineClass').outgoing:
            if rel.end['name'] == className:
                return rel.end

        return defineClass(className)


    def setClass(node, className):
        getattr(node, 'class')(getClassNode(className))



