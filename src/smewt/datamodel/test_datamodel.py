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
from baseobject import BaseObject
import ontology
import unittest

class TestObjectNode(unittest.TestCase):

    def testBasicObjectNode(self):
        g = MemoryObjectGraph()
        n1 = g.BaseObject()
        self.assertEqual(n1.keys(), [])

        n1.title = 'abc'
        self.assertEqual(n1.title, 'abc')

        n2 = g.BaseObject(title = 'abc')
        self.assertEqual(n2.title, 'abc')
        self.assertEqual(n1, n2)

        n1.sameas = n2
        self.assertEqual(n1.sameas, n2)

        n2.plot = 'empty'
        self.assertEqual(n1.sameas.title, 'abc')
        self.assertEqual(n1.sameas.plot, 'empty')

    def testBasicOntology(self):
        class A(BaseObject):
            schema = { 'title': unicode  }
            valid = schema.keys()
            unique = valid

        class B(A):
            pass

        class C(BaseObject):
            schema = { 'c': int  }
            valid = schema.keys()
            unique = valid

        class D(BaseObject):
            pass

        class E:
            schema = { 'e': int  }
            unique = [ 'e' ]

        self.assertEqual(issubclass(A, BaseObject), True)
        self.assertEqual(issubclass(B, A), True)
        self.assertEqual(issubclass(A, A), True)
        self.assertEqual(issubclass(A, B), False)
        self.assertEqual(issubclass(B, BaseObject), True)
        self.assertEqual(issubclass(C, A), False)
        self.assertEqual(B.parentClass().className(), 'A')

        ontology.register(A, B, C)
        #self.assertRaises(TypeError, ontology.register, D) # put this later on again
        self.assertRaises(TypeError, ontology.register, E)

        self.assert_(ontology.getClass('A') is A)
        self.assertRaises(ValueError, ontology.getClass, 'D')
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

            reverseLookup = { 'series': 'episodes' }
            valid = [ 'series', 'season', 'episodeNumber' ]
            unique = valid

        class Person(BaseObject):
            schema = { 'firstName': unicode,
                       'lastName': unicode,
                       'dateOfBirth': float, # TODO: should be datetime
                       }

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
            reverseLookup = { 'director': 'filmography' }

        class Character(BaseObject):
            schema = { 'name': unicode }
            valid = schema.keys()

        class Role(BaseObject):
            schema = { 'movie': Movie,
                       'actor': Person,
                       'character': Character
                       }

            reverseLookup = { 'movie': 'roles',
                              'actor': 'actingRoles',
                              'character': 'roles'
                              }

        # register all these classes onto the global ontology
        ontology.register(Series, Episode, Person, Movie, Character, Role)


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
        self.assert_(n1 in g)
        self.assert_(n3 in g)
        self.assert_(n4 not in g)

    def testGraphTransfer(self):
        g1 = MemoryObjectGraph()
        g2 = MemoryObjectGraph()

        n1 = g1.BaseObject(a = 23)
        n2 = g1.BaseObject(friend = n1)

        # by default we use recurse = OnIdentity
        # we could also have g2.addNode(n2, recurse = OnValue) or recurse = OnUnique
        r2 = g2.addNode(n2)
        self.assert_(r2 in g2)
        # verify it also brought its friend
        self.assert_(r2.friend in g2)
        self.assertEqual(r2.friend.a, 23)

        # if we keep on adding by identity, we will end up with lots of friends with a=23
        n3 = g1.BaseObject(name = 'other node', friend = n1)
        r3 = g2.addNode(n3)
        self.assertEquals(len(g2.findAll(a = 23)), 2)

        # if we add and recurse on value, we shouldn't be adding the same node again and again
        n4 = g1.BaseObject(name = '3rd of its kind', friend = n1)
        r4 = g2.addNode(n4, recurse = Equal.OnValue)

        self.assertEquals(len(g2.findAll(a = 23)), 2) # no new node added with a = 23
        # reference should have been updated though, no trying to keep old friends
        self.assert_(r4.friend._node == r2.friend._node or r4.friend._node == r3.friend._node)


    def atestReverseAttributeLookup(self):
        """not valid test anymore, needs updating"""
        g = MemoryObjectGraph()

        n1 = g.BaseObject(x = 1)
        n2 = g.BaseObject(x = 2, friend = n1)

        self.assertEqual(n2.friend, n1)
        self.assertRaises(AttributeError, getattr, n1, 'is_friend_of')

        g = ObjectGraph()
        g.addNode(n2) # this should also add n1 recursively
        self.assert_(n2 in g)
        self.assert_(n1 in g)
        self.assertEqual(n1.is_friend_of, n2)


    def createData(self, g):
        g.Movie(title = 'Fear and Loathing in Las Vegas')
        g.Movie(title = 'The Dark Knight')


    def testFindObjectsInGraph(self):
        self.registerMediaOntology()

        Movie = ontology.getClass('Movie')
        Episode = ontology.getClass('Episode')
        Person = ontology.getClass('Person')
        Character = ontology.getClass('Character')

        g = MemoryObjectGraph()
        self.createData(g)

        print g.findAll(type = Movie)
        '''
        g.findAll(Episode, lambda x: x.season == 2)
        g.findAll(Episode, season = 2)
        g.findall(Movie, lambda m: m.release_year > 2000)
        g.findAll(Person, role_movie_title = 'The Dark Knight') # role == Role.isPersonOf
        g.findAll(Character, isCharacterOf_movie_title = 'Fear and Loathing in Las Vegas', regexp = True)
        g.findAll(Character, roles_movie_title = 'Fear and loathing.*', regexp = True)
        print c.isCharacterOf.movie.title
        print c.is_character_of.movie.title
        '''


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestObjectNode)
    unittest.TextTestRunner(verbosity=2).run(suite)
