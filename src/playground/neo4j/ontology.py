#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import with_statement
import smewtdb


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


# dictionary that keeps the class names and their resp. nodes and Delegator subclasses
_classes = {}

def register(*args):
    with smewtdb.transaction:
        for c in args:
            # tuple of derived Class object, class node in neo4j
            _classes[c.__name__] = (c, getClassNode(c.__name__))
