#!/usr/bin/env python

from __future__ import with_statement
from smewtobjectmapper import *
import smewtdb, ontology

# we should define a separate object-model library, which would allow to define
# a loose ontology (a-la django, but only semi-structured) and which would have
# an option to have the object persistent or not (ie: just old-school smewt in
# memory, or stored inside neo4j.


smewtdb.deleteAllData()
smewtdb.init()


class Series(Delegator):
    def __unicode__(self):
        return self.title


class Episode(Delegator):
    pass


ontology.register(Series, Episode)

s = Series(title = 'Scrubs')
e = Episode(season = 3, number = 2)
e2 = Episode(series = s)

print '*'*100
print type(s)
print e2.series

print 's ok'

print '*'*100
printAllNodes()

smewtdb.shutdown()
#ep1 = Episode(season = 2, number = 3, series = s)

