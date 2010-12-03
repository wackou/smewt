#!/usr/bin/env python

from __future__ import with_statement
from neo4j._primitives import Node
import smewtdb, ontology

# we should define a separate object-model library, which would allow to define
# a loose ontology (a-la django, but only semi-structured) and which would have
# an option to have the object persistent or not (ie: just old-school smewt in
# memory, or stored inside neo4j.


def nodeToString(n):
    attrs = [ '%s=%s' % (key, value) for key, value in n.items() ]

    rels = [ '%s=%s' % (rel.type, nodeToString(rel.end))
             for rel in n.relationships().outgoing if rel.type != 'class' ]

    return '%s(id=%d, %s)' % (ontology.getClassName(n), n.id, ', '.join(attrs + rels))

def printNode(n):
    print nodeToString(n)

# print all nodes
def printAllNodes():
    with smewtdb.transaction:
        try:
            for n in smewtdb.neo.node:
                printNode(n)
        except:
            pass




def printClasses():
    print '*'*60
    print 'Classes:'
    for classrel in smewtdb.neo.reference_node.relationships('defineClass').outgoing:
        print classrel.end['name']
    print '*'*60


def wrapNode(n):
    className = list(n.relationships('class').outgoing)[0].end['name']
    return ontology._classes[className][0](n)


class Delegator:
    """TODO: make sure we don't have both a property *and* a relationship with the
    same name"""

    def __init__(self, node = None, **kwargs):
        with smewtdb.transaction:
            if node and not kwargs:
                self._node = node
                return

            self._node = smewtdb.neo.node()
            ontology.setClass(self._node, self.__class__.__name__)

            for key, value in kwargs.items():
                setattr(self, key, value)

    def __setattr__(self, name, value):
        if name == '_node':
            self.__dict__[name] = value
            return

        self.set(name, value)

    def setValidate(self, name, value):
        raise NotImplementedError()

    def set(self, name, value):
        print 'set', name, value
        # if we set the property to a node, then we want to make it a relationship
        # otherwise, it's just a simple property
        if isinstance(value, Delegator):
            getattr(self._node, name)(value._node)
        elif isinstance(value, Node):
            print getattr(self._node, name)
            getattr(self._node, name)(value)
        else:
            self._node[name] = value


    def __getattr__(self, name):
        if name == '_node':
            return self.__dict__[name]

        result = self.get(name)
        print 'result', result
        if result is not None:
            return result

        raise AttributeError, name

    def get(self, name):
        """Returns the given property, None if not found."""
        try:
            return self._node[name]
        except:
            result = list(self._node.relationships(name))
            if not result: return None
            if len(result) == 1: return wrapNode(result[0].end)
            return result


    def __str__(self):
        return '%s(%s)' % (ontology.getClassName(self._node), unicode(self))
