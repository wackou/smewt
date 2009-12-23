#!/usr/bin/env python

from __future__ import with_statement
from neo4j import NeoService
from neo4j._primitives import Node

# we should define a separate object-model library, which would allow to define
# a loose ontology (a-la django, but only semi-structured) and which would have
# an option to have the object persistent or not (ie: just old-school smewt in
# memory, or stored inside neo4j.

NEO_DB = '/tmp/gloub'

neo = None

def init():
    global neo
    neo = NeoService(NEO_DB,
                     jvm = '/usr/lib/jvm/java-6-openjdk/jre/lib/i386/client/libjvm.so')


def shutdown():
    global neo
    neo.shutdown()
    neo = None

def cleanDB():
    global neo
    try:
        neo.shutdown()
    except: pass
    
    import subprocess
    subprocess.call([ 'rm', '-fr', NEO_DB ])

    init()
    



def getClassName(n):
    try:
        return list(n.relationships('class').outgoing)[0].end['name']
    except:
        return 'Node'


def nodeToString(n):
    attrs = [ '%s=%s' % (key, value) for key, value in n.items() ]

    rels = [ '%s=%s' % (rel.type, nodeToString(rel.end))
             for rel in n.relationships().outgoing if rel.type != 'class' ]
    
    return '%s(id=%d, %s)' % (getClassName(n), n.id, ', '.join(attrs + rels))

def printNode(n):
    print nodeToString(n)

# print all nodes
def printAllNodes():
    with neo.transaction:
        try:
            for n in neo.node:
                printNode(n)
        except:
            pass


def defineClass(className):
    cnode = neo.node(name = className)
    neo.reference_node.defineClass(cnode)
    #setClass(cnode, 'Class') # cannot have rel.start == rel.end
    return cnode

def getClassNode(className):
    # TODO: should be cached
    for rel in neo.reference_node.relationships('defineClass').outgoing:
        if rel.end['name'] == className:
            return rel.end

    return defineClass(className)


def setClass(node, className):
    getattr(node, 'class')(getClassNode(className))


def printClasses():
    print '*'*60
    print 'Classes:'
    for classrel in neo.reference_node.relationships('defineClass').outgoing:
        print classrel.end['name']
    print '*'*60


class Ontology:
    classes = {}

    @staticmethod
    def register(*args):
        with neo.transaction:
            for c in args:
                # tuple of derived Class object, class node in neo4j
                Ontology.classes[c.__name__] = (c, getClassNode(c.__name__))


def wrapNode(n):
    className = list(n.relationships('class').outgoing)[0].end['name']
    return Ontology.classes[className][0](n)


class Delegator:
    """TODO: make sure we don't have both a property *and* a relationship with the
    same name"""
    
    def __init__(self, node = None, **kwargs):
        with neo.transaction:
            if node and not kwargs:
                self._node = node
                return
            
            self._node = neo.node()
            setClass(self._node, self.__class__.__name__)

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
        return '%s(%s)' % (getClassName(self._node), unicode(self))
