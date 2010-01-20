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

from objectnode import ObjectNode
from objectgraph import ObjectGraph, Equal
from memoryobjectgraph import MemoryObjectGraph
from baseobject import BaseObject, Schema
from utils import tolist
import ontology
import unittest

class TestObjectNode(unittest.TestCase):

    def setUp(self):
        # FIXME: clear the previous ontology because the graphs do not get GC-ed properly
        ontology.clear()

    def testBasicObjectNode(self):
        g = MemoryObjectGraph()
        n1 = g.BaseObject()
        self.assertEqual(n1.keys(), [])

        n1.title = u'abc'
        self.assertEqual(n1.title, u'abc')

        n2 = g.BaseObject(title = u'abc')
        self.assertEqual(n2.title, u'abc')
        self.assertEqual(n1, n2)

        n1.sameas = n2
        # make sure there's no ambiguity between ObjectNodes and BaseObjects
        self.assertEqual(n1.sameas, n2)
        self.assert_(n2._node in n1._node.sameas)
        self.assert_(n2 not in n1._node.sameas)
        self.assertNotEqual(n1.sameas, n2._node)
        self.assertEqual(BaseObject(n1.sameas), n2)

        n2.plot = u'empty'
        self.assertEqual(n1.sameas.title, u'abc')
        self.assertEqual(n1.sameas.plot, u'empty')

    def testBasicOntology(self):
        class A(BaseObject):
            schema = Schema({ 'title': unicode })
            valid = schema.keys()
            unique = valid

        class B(A):
            pass

        class C(BaseObject):
            schema = Schema({ 'c': int })
            valid = schema.keys()
            unique = valid

        class D(BaseObject):
            pass

        class E:
            schema = Schema({ 'e': int })
            unique = [ 'e' ]

        self.assertEqual(issubclass(A, BaseObject), True)
        self.assertEqual(issubclass(B, A), True)
        self.assertEqual(issubclass(A, A), True)
        self.assertEqual(issubclass(A, B), False)
        self.assertEqual(issubclass(B, BaseObject), True)
        self.assertEqual(issubclass(C, A), False)
        self.assertEqual(B.parentClass().className(), 'A')

        ontology.register(A, B, C)
        self.assertRaises(TypeError, ontology.register, E) # should inherit from BaseObject

        self.assert_(ontology.getClass('A') is A)
        self.assertRaises(ValueError, ontology.getClass, 'D') # not registered
        self.assert_(ontology.getClass('B').parentClass().parentClass() is BaseObject)

        # test instance creation
        g = MemoryObjectGraph()
        a = g.A(title = u'Scrubs', epnum = 5)

        self.assertEqual(type(a), A)
        self.assertEqual(a.__class__, A)
        self.assertEqual(a.__class__.className(), 'A')
        self.assertEqual(a.__class__.__name__, 'A')

    def registerMediaOntology(self):
        class Series(BaseObject):
            schema = Schema({ 'title': unicode,
                              'rating': float
                              })

            valid = [ 'title' ]
            unique = valid

        class Episode(BaseObject):
            schema = Schema({ 'series': Series,
                              'season': int,
                              'episodeNumber': int,
                              'title': unicode,
                              'synopsis': unicode
                              })

            reverseLookup = { 'series': 'episodes' }
            valid = [ 'series', 'season', 'episodeNumber' ]
            unique = valid

            def __cmp__(self, other):
                return (self.season - other.season) or (self.episodeNumber - other.episodeNumber)

        class Person(BaseObject):
            schema = Schema({ 'firstName': unicode,
                              'lastName': unicode,
                              'dateOfBirth': float, # TODO: should be datetime
                              })
            valid = [ 'firstName', 'lastName' ]

            def name(self):
                return self.firstName + ' ' + self.lastName

            def bestMovie(self):
                """This returns the movie with the highest rating this actor has played in"""
                ratings = [ (role.movie.imdbRating, role.movie) for role in tolist(self.role) ]
                return sorted(ratings)[-1][1]


        class Movie(BaseObject):
            schema = Schema({ 'title': unicode,
                              'year': int,
                              'plot': unicode,
                              'imdbRating': float,
                              'director': Person,
                              })
            reverseLookup = { 'director': 'filmography' }
            valid = [ 'title', 'year' ]
            unique = valid

        class Character(BaseObject):
            schema = Schema({ 'name': unicode })
            valid = schema.keys()

        class Role(BaseObject):
            schema = Schema({ 'movie': Movie,
                              'actor': Person,
                              'character': Character
                              })
            reverseLookup = { 'movie': 'roles',
                              'actor': 'actingRoles',
                              'character': 'roles'
                              }
            valid = schema.keys()
            unique = valid

        # register all these classes onto the global ontology
        # until this is done automatically, we need to make sure they are registered in the same order as they are defined
        # otherwise it might lead to subtle problems, such as reverse properties that can't be found.
        ontology.register(Series, Episode, Person, Movie, Character, Role)


    def testMediaOntology(self):
        self.registerMediaOntology()

        Series = ontology.getClass('Series')
        Episode = ontology.getClass('Episode')
        Person = ontology.getClass('Person')

        self.assert_('episodes' in Series.schema)
        self.assert_('episodes' in Series.reverseLookup)
        self.assertEqual(Person.schema['filmography'], ontology.getClass('Movie'))
        self.assertEqual(Person.reverseLookup['filmography'], 'director')

        g = MemoryObjectGraph()
        self.createData(g)

        ep = g.findOne(Episode)
        # Series needs only 'title', so it should be a fit
        self.assertEqual(ep._node, Series(ep)._node)

        s = g.findOne(Series)
        self.assertRaises(TypeError, Episode, s)

    def testValidUniqueMethods(self):
        self.registerMediaOntology()

        g = MemoryObjectGraph()
        ep = g.Episode(series = g.Series(title = u'House M.D.'), season = 3, episodeNumber = 2)
        self.assertRaises(TypeError, g.Episode, series = u'House M.D.', episodeNumber = 2)
        #self.assertEqual(ep.isValid(), True) # construction of object should fail if not
        ep.title = u'gloub'
        ep.gulp = u'gloubiboulga'
        #self.assertEqual(ep.isValid(), True)
        self.assertRaises(TypeError, setattr, ep, 'title', 3)
        #self.assertEqual(ep.isValid(), False)

        self.assertEqual(ep.isUnique(), True)
        #self.assertEqual(g.Episode(series=u'abc').isUnique(), False)

    def testBasicGraphBehavior(self):
        g = MemoryObjectGraph()
        g2 = MemoryObjectGraph()

        n1 = g.BaseObject(x = 1)
        self.assert_(n1._node in g)
        n2 = g.BaseObject(x = 1)
        n3 = g.BaseObject(n1)
        n4 = g2.BaseObject(n1)

        # equality of objects should be based on value
        self.assertEqual(n1, n2)
        self.assertEqual(n1, n3)
        self.assertEqual(n1, n4)

        # equality of nodes should be based on identity
        self.assertEqual(n1._node, n3._node)
        self.assertNotEqual(n1._node, n2._node)
        self.assertNotEqual(n1._node, n4._node) # not equal as they live in different graphs

        # graph belonging should be tested with identity (related to node)
        self.assert_(n1._node in g)
        self.assert_(n3 in g)
        self.assert_(n4 not in g)


    def testGraphTransfer(self):
        class NiceGuy(BaseObject):
            schema = Schema({ 'friend': BaseObject })
            valid = [ 'friend' ]
            reverseLookup = { 'friend': 'friend' }

        ontology.register(NiceGuy)

        g1 = MemoryObjectGraph()
        g2 = MemoryObjectGraph()

        n1 = g1.BaseObject(a = 23)
        n2 = g1.NiceGuy(friend = n1)

        # by default we use recurse = OnIdentity
        # we could also have g2.addObject(n2, recurse = OnValue) or recurse = OnUnique
        r2 = g2.addObject(n2)
        self.assert_(r2 in g2)
        # verify it also brought its friend
        self.assert_(r2.friend in g2)
        self.assertEqual(r2.friend.a, 23)
        self.assertEquals(len(g2.findAll(a = 23)), 1)

        # FIXME: the following fails, it surely hides a bug...
        # if we keep on adding by identity, we will end up with lots of friends with a=23
        #n3 = g1.BaseObject(name = u'other node', friend = n1)
        #r3 = g2.addObject(n3)
        #self.assertEquals(len(g2.findAll(a = 23)), 2)

        # if we keep on adding by identity, we will end up with lots of friends with a=23
        n3 = g1.NiceGuy(name = u'other node', friend = n1)
        r3 = g2.addObject(n3)
        self.assertEquals(len(g2.findAll(a = 23)), 2)

        # if we add and recurse on value, we shouldn't be adding the same node again and again
        n4 = g1.NiceGuy(name = u'3rd of its kind', friend = g1.BaseObject(a = 23))

        r4 = g2.addObject(n4, recurse = Equal.OnValue)

        self.assertEquals(len(g2.findAll(a = 23)), 2) # no new node added with a = 23
        # reference should have been updated though, no trying to keep old friends
        self.assert_(r4.friend._node in [ r._node for r in tolist(r2.friend) ] or
                     r4.friend._node in [ r._node for r in tolist(r3.friend) ])


    def testReverseAttributeLookup(self):
        self.registerMediaOntology()

        Series = ontology.getClass('Series')
        Episode = ontology.getClass('Episode')

        g = MemoryObjectGraph()
        self.createData(g)

        s = g.findOne(Series, title = u'The Wire')
        self.assertEqual(s, s.episodes[0].series)

        ep = g.findOne(Episode)
        self.assert_(ep in ep.series.episodes)

        # make sure auto-reverse name work correctly
        vador = g.BaseObject(side = u'dark')
        luke = g.BaseObject(side = u'light', father = vador)

        self.assertEqual(luke.father.side, u'dark')
        self.assertEqual(vador.isFatherOf.side, u'light')


    def createData(self, g):
        g.Movie(title = u'Fear and Loathing in Las Vegas', year = 1998)
        g.Movie(title = u'The Dark Knight', year = 2008)

        wire = g.Series(title = u'The Wire')

        g.Episode(series = wire,
                  season = 2,
                  episodeNumber = 1,
                  title = u'Ebb Tide')

        g.Episode(series = wire,
                  season = 2,
                  episodeNumber = 2,
                  title = u'Collateral Damage')


    def testFindObjectsInGraph(self):
        self.registerMediaOntology()

        Movie = ontology.getClass('Movie')
        Series = ontology.getClass('Series')
        Episode = ontology.getClass('Episode')
        Person = ontology.getClass('Person')
        Character = ontology.getClass('Character')

        g = MemoryObjectGraph()
        self.createData(g)

        self.assertEqual(len(g.findAll(type = Movie)), 2)
        self.assertEqual(len(g.findAll(Episode, lambda x: x.season == 2)), 2)
        self.assertEqual(len(g.findAll(Episode, season = 2)), 2)
        self.assertEqual(g.findOne(Episode, season = 2, episodeNumber = 1).title, 'Ebb Tide')
        e = g.findOne(Episode, season = 2, episodeNumber = 1)

        recentMovies = g.findAll(Movie, lambda m: m.year > 2000)
        self.assertEqual(len(recentMovies), 1)
        self.assertEqual(recentMovies[0].title, 'The Dark Knight')

        self.assertEqual(len(g.findAll(Episode, series_title = 'The Wire')), 2)
        thewire = g.findOne(Series, title = 'The Wire')
        self.assertEqual(len(g.findAll(Episode, series = thewire)), 2)
        '''
        g.findAll(Person, role_movie_title = 'The Dark Knight') # role == Role.isPersonOf
        g.findAll(Character, isCharacterOf_movie_title = 'Fear and Loathing in Las Vegas', regexp = True)
        g.findAll(Character, roles_movie_title = 'Fear and loathing.*', regexp = True)
        print c.isCharacterOf.movie.title
        print c.is_character_of.movie.title
        '''

    def testComplexGraph(self):
        self.registerMediaOntology()

        Movie = ontology.getClass('Movie')
        Series = ontology.getClass('Series')
        Episode = ontology.getClass('Episode')
        Person = ontology.getClass('Person')
        Character = ontology.getClass('Character')

        g = MemoryObjectGraph()

        e = g.Episode(series = g.Series(title = u'abc'), season = 1, episodeNumber = 23)
        g.findOrCreate(Series, title = u'def')

        self.assertEqual(len(g.findAll(Series)), 2)

        e2 = g.Episode(series = g.findOrCreate(Series, title = u'abc'), season = 1, episodeNumber = 34)

        s = g.findOne(Series, title = u'abc')
        self.assertEqual(len(s.episodes), 2)

        # test that methos on BaseObjects subclasses are correctly called. In our case: Episode.__cmp__
        ep1 = g.Episode(series = s, season = 1, episodeNumber = 1)
        ep2 = g.Episode(series = s, season = 1, episodeNumber = 2)
        ep3 = g.Episode(series = s, season = 1, episodeNumber = 3)
        ep4 = g.Episode(series = s, season = 1, episodeNumber = 4)
        ep5 = g.Episode(series = s, season = 1, episodeNumber = 5)

        self.assertEqual(sorted(s.episodes), [ ep1, ep2, ep3, ep4, ep5, e, e2 ])


    def atestNeo4j(self):
        from neo4jobjectgraph import Neo4jObjectGraph

        self.registerMediaOntology()
        g = Neo4jObjectGraph('/tmp/gloub')
        g.clear()


        Movie = ontology.getClass('Movie')
        print 'creating movie'
        m = g.Movie(title = u'hello')
        print 'movie created'

        g.close()

        g2 = Neo4jObjectGraph('/tmp/gloub')




if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestObjectNode)

    import logging
    logging.getLogger('smewt').setLevel(logging.WARNING)
    logging.getLogger('smewt.datamodel.Ontology').setLevel(logging.ERROR)
    #logging.getLogger('smewt.datamodel.Neo4jObjectNode').setLevel(logging.DEBUG)
    #logging.getLogger('smewt.datamodel.ObjectNode').setLevel(logging.DEBUG)

    unittest.TextTestRunner(verbosity=2).run(suite)
