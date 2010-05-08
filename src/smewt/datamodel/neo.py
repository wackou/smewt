#!/usr/bin/env python
# -*- coding: utf-8 -*-

from neo4j import NeoService
import subprocess, glob
import logging

log = logging.getLogger('smewt.datamodel.Neo4j')


dirname = None
graph = None
transaction = None


def defaultJVM():
    # make an educated guess on debian-based system
    java = subprocess.Popen([ 'ls', '-l', '/etc/alternatives/java' ], stdout = subprocess.PIPE).stdout.read().strip().split()[-1]
    java_rootdir = '/'.join(java.split('/')[:-2])
    jvms = glob.glob(java_rootdir + '/lib/*/client/libjvm.so')

    if jvms:
        return jvms[0]

    raise OSError, 'Could not find default JVM'



def close():
    global dirname, graph, transaction

    try:
        graph.shutdown()
        dirname, graph, transaction = None, None, None
    except RuntimeError, e:
        log.error(str(e))


def open(dbpath):
    global dirname, graph, transaction

    if dirname:
        raise RuntimeError("A Neo4j database is already open. Please close it before opening a new one.")

    dirname = dbpath
    graph = NeoService(dbpath, jvm = defaultJVM())
    transaction = graph.transaction


def deleteAllData():
    global dirname
    dbpath = dirname

    close()

    print dbpath, type(dbpath)
    # do it the brute-force way...
    subprocess.call([ 'rm', '-fr', dbpath ])

    open(dbpath)

