#!/usr/bin/env python
# -*- coding: utf-8 -*-

from neo4j import NeoService
import subprocess, glob

NEO_DB = '/tmp/gloub'

neo = None
transaction = None


def defaultJVM():
    # make an educated guess on debian-based system
    java = subprocess.Popen([ 'ls', '-l', '/etc/alternatives/java' ], stdout = subprocess.PIPE).stdout.read().strip().split()[-1]
    java_rootdir = '/'.join(java.split('/')[:-2])
    jvms = glob.glob(java_rootdir + '/lib/*/client/libjvm.so')

    if jvms:
        return jvms[0]

    raise OSError, 'Could not find default JVM'


def init():
    global neo, transaction
    neo = NeoService(NEO_DB, jvm = defaultJVM())
    transaction = neo.transaction


def shutdown():
    global neo, transaction
    neo.shutdown()
    neo, transaction = None, None


def deleteAllData():
    try:
        shutdown()
    except: pass

    # do it the brute-force way...
    subprocess.call([ 'rm', '-fr', NEO_DB ])

