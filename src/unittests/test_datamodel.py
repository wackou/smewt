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


import logging
logging.getLogger('smewt').setLevel(logging.WARNING)

from smewttest import *

class TestObjectNode(TestCase):

    def setUp(self):
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
        self.assert_(n2.node in n1.node.sameas)
        self.assert_(n2 not in n1.node.sameas)
        self.assertNotEqual(n1.sameas, n2.node)
        self.assertEqual(BaseObject(n1.sameas), n2)

        n2.plot = u'empty'
        self.assertEqual(n1.sameas.title, u'abc')
        self.assertEqual(n1.sameas.plot, u'empty')

    def testBasicOntology(self):
        class A(BaseObject):
            schema = { 'title': unicode }
            valid = schema.keys()
            unique = valid

        class B(A):
            schema = {}
            #valid = [ 'title' ]
            valid = A.valid
            unique = [ 'title' ]

        class C(BaseObject):
            schema = { 'c': int }
            valid = schema.keys()
            unique = valid

        class D(BaseObject):
            schema = {}
            valid = []

        class E:
            schema = { 'e': int }
            unique = [ 'e' ]

        class F(BaseObject):
            schema = { 'friend': BaseObject }
            reverse_lookup = { 'friend': 'friend' }
            valid = schema.keys()

        self.assertEqual(issubclass(A, BaseObject), True)
        self.assertEqual(issubclass(B, A), True)
        self.assertEqual(issubclass(A, A), True)
        self.assertEqual(issubclass(A, B), False)
        self.assertEqual(issubclass(B, BaseObject), True)
        self.assertEqual(issubclass(C, A), False)
        self.assertEqual(B.parent_class().class_name(), 'A')

        #self.assertRaises(TypeError, ontology.register, E) # should inherit from BaseObject
        # should not define the same reverse_lookup name when other class is a superclass (or subclass) of our class
        self.assertRaises(TypeError, ontology.register, F)

        self.assert_(ontology.get_class('A') is A)
        #self.assertRaises(ValueError, ontology.get_class, 'D') # not registered
        self.assert_(ontology.get_class('B').parent_class().parent_class() is BaseObject)

        # test instance creation
        g = MemoryObjectGraph()
        a = g.A(title = u'Scrubs', epnum = 5)

        self.assertEqual(type(a), A)
        self.assertEqual(a.__class__, A)
        self.assertEqual(a.__class__.class_name(), 'A')
        self.assertEqual(a.__class__.__name__, 'A')

    def registerMediaOntology(self):
        class Series(BaseObject):
            schema = { 'title': unicode,
                       'rating': float
                       }

            valid = [ 'title' ]
            unique = valid

        class Episode(BaseObject):
            schema = { 'series': Series,
                       'season': int,
                       'episodeNumber': int,
                       'title': unicode,
                       'synopsis': unicode
                       }

            reverse_lookup = { 'series': 'episodes' }
            valid = [ 'series', 'season', 'episodeNumber' ]
            unique = valid

            def __cmp__(self, other):
                return (self.season - other.season) or (self.episodeNumber - other.episodeNumber)

        class Person(BaseObject):
            schema = { 'firstName': unicode,
                       'lastName': unicode,
                       'dateOfBirth': float, # TODO: should be datetime
                       }
            valid = [ 'firstName', 'lastName' ]

            def name(self):
                return self.firstName + ' ' + self.lastName

            def bestMovie(self):
                """This returns the movie with the highest rating this actor has played in"""
                ratings = [ (role.movie.imdbRating, role.movie) for role in tolist(self.role) ]
                return sorted(ratings)[-1][1]


        class Movie(BaseObject):
            schema = { 'title': unicode,
                       'year': int,
                       'plot': unicode,
                       'imdbRating': float,
                       'director': Person,
                       }
            reverse_lookup = { 'director': 'filmography' }
            valid = [ 'title', 'year' ]
            unique = valid

        class Character(BaseObject):
            schema = { 'name': unicode }
            valid = schema.keys()

        class Role(BaseObject):
            schema = { 'movie': Movie,
                       'actor': Person,
                       'character': Character
                       }
            reverse_lookup = { 'movie': 'roles',
                              'actor': 'actingRoles',
                              'character': 'roles'
                              }
            valid = schema.keys()
            unique = valid


    def testMediaOntology(self):
        self.registerMediaOntology()
        ontology.import_classes([ 'Series', 'Episode', 'Person' ])

        self.assert_('episodes' in Series.schema)
        self.assert_('episodes' in Series.reverse_lookup)
        self.assertEqual(Person.schema['filmography'], ontology.get_class('Movie'))
        self.assertEqual(Person.reverse_lookup['filmography'], 'director')

        g = MemoryObjectGraph(dynamic = True)
        self.createData(g)

        ep = g.find_one(Episode)
        # Series needs only 'title', so it should be a fit if the graph is dynamic
        self.assertEqual(ep.node, Series(ep).node)

        s = g.find_one(Series, title = 'The Wire')
        self.assertRaises(TypeError, Episode, s)


        # test with a static graph
        g = MemoryObjectGraph(dynamic = False)
        self.createData(g)

        ep = g.find_one(Episode)
        # Series needs only 'title', so it should be a fit if the graph is dynamic
        self.assertRaises(TypeError, Series, ep)

        s = g.find_one(Series)
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

        self.assertEqual(ep.is_unique(), True)
        #self.assertEqual(g.Episode(series=u'abc').is_unique(), False)

    def testBasicGraphBehavior(self):
        g = MemoryObjectGraph()
        g2 = MemoryObjectGraph()

        n1 = g.BaseObject(x = 1)
        self.assert_(n1.node in g)
        n2 = g.BaseObject(x = 1)
        n3 = g.BaseObject(n1)
        n4 = g2.BaseObject(n1)

        # equality of objects should be based on value
        self.assertEqual(n1, n2)
        self.assertEqual(n1, n3)
        self.assertEqual(n1, n4)

        # equality of nodes should be based on identity
        self.assertEqual(n1.node, n3.node)
        self.assertNotEqual(n1.node, n2.node)
        self.assertNotEqual(n1.node, n4.node) # not equal as they live in different graphs

        # graph belonging should be tested with identity (related to node)
        self.assert_(n1.node in g)
        self.assert_(n3 in g)
        self.assert_(n4 not in g)


    def testGraphTransfer(self):
        class NiceGuy(BaseObject):
            schema = { 'friend': BaseObject }
            valid = [ 'friend' ]
            reverse_lookup = { 'friend': 'friendOf' }

        g1 = MemoryObjectGraph()
        g2 = MemoryObjectGraph()

        n1 = g1.BaseObject(a = 23)
        n2 = g1.NiceGuy(friend = n1)

        # by default we use recurse = OnIdentity
        # we could also have g2.add_object(n2, recurse = OnValue) or recurse = OnUnique
        r2 = g2.add_object(n2)
        self.assert_(r2 in g2)
        # verify it also brought its friend
        self.assert_(r2.friend in g2)
        self.assertEqual(r2.friend.a, 23)
        self.assertEquals(len(g2.find_all(a = 23)), 1)

        # FIXME: the following fails, it surely hides a bug...
        # if we keep on adding by identity, we will end up with lots of friends with a=23
        #n3 = g1.BaseObject(name = u'other node', friend = n1)
        #r3 = g2.add_object(n3)
        #self.assertEquals(len(g2.find_all(a = 23)), 2)

        # if we keep on adding by identity, we will end up with lots of friends with a=23
        n3 = g1.NiceGuy(name = u'other node', friend = n1)
        r3 = g2.add_object(n3)
        self.assertEquals(len(g2.find_all(a = 23)), 2)

        # if we add and recurse on value, we shouldn't be adding the same node again and again
        n4 = g1.NiceGuy(name = u'3rd of its kind', friend = g1.BaseObject(a = 23))

        r4 = g2.add_object(n4, recurse = Equal.OnValue)

        self.assertEquals(len(g2.find_all(a = 23)), 2) # no new node added with a = 23
        # reference should have been updated though, no trying to keep old friends
        self.assert_(r4.friend.node in [ r.node for r in tolist(r2.friend) ] or
                     r4.friend.node in [ r.node for r in tolist(r3.friend) ])


    def testReverseAttributeLookup(self):
        self.registerMediaOntology()
        ontology.import_classes([ 'Series', 'Episode' ])

        g = MemoryObjectGraph()
        self.createData(g)

        s = g.find_one(Series, title = u'The Wire')
        self.assertEqual(s, s.episodes[0].series)

        ep = g.find_one(Episode)
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
        ontology.import_classes([ 'Movie', 'Series', 'Episode', 'Person', 'Character' ])

        g = MemoryObjectGraph()
        self.createData(g)

        self.assertEqual(len(g.find_all(type = Movie)), 2)
        self.assertEqual(len(g.find_all(Episode, lambda x: x.season == 2)), 2)
        self.assertEqual(len(g.find_all(Episode, season = 2)), 2)
        self.assertEqual(g.find_one(Episode, season = 2, episodeNumber = 1).title, 'Ebb Tide')
        e = g.find_one(Episode, season = 2, episodeNumber = 1)

        recentMovies = g.find_all(Movie, lambda m: m.year > 2000)
        self.assertEqual(len(recentMovies), 1)
        self.assertEqual(recentMovies[0].title, 'The Dark Knight')

        self.assertEqual(len(g.find_all(Episode, series_title = 'The Wire')), 2)
        thewire = g.find_one(Series, title = 'The Wire')
        self.assertEqual(len(g.find_all(Episode, series = thewire)), 2)
        '''
        g.find_all(Person, role_movie_title = 'The Dark Knight') # role == Role.isPersonOf
        g.find_all(Character, isCharacterOf_movie_title = 'Fear and Loathing in Las Vegas', regexp = True)
        g.find_all(Character, roles_movie_title = 'Fear and loathing.*', regexp = True)
        print c.isCharacterOf.movie.title
        print c.is_character_of.movie.title
        '''

    def testComplexGraph(self):
        self.registerMediaOntology()
        ontology.import_classes([ 'Movie', 'Series', 'Episode', 'Person', 'Character' ])

        g = MemoryObjectGraph()

        e = g.Episode(series = g.Series(title = u'abc'), season = 1, episodeNumber = 23)
        g.find_or_create(Series, title = u'def')

        self.assertEqual(len(g.find_all(Series)), 2)

        e2 = g.Episode(series = g.find_or_create(Series, title = u'abc'), season = 1, episodeNumber = 34)

        s = g.find_one(Series, title = u'abc')
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


        Movie = ontology.get_class('Movie')
        print 'creating movie'
        m = g.Movie(title = u'hello')
        print 'movie created'

        g.close()

        g2 = Neo4jObjectGraph('/tmp/gloub')


suite = allTests(TestObjectNode)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)