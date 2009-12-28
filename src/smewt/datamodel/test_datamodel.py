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
from memoryobjectgraph import MemoryObjectGraph
from ontology import BaseObject, OntologyManager
import unittest

class TestObjectNode(unittest.TestCase):

    def testBasicObjectNode(self):
        print 'a'
        g = MemoryObjectGraph()
        n1 = g.BaseObject()
        self.assertEquals(n1.keys(), [])

        n1.title = 'abc'
        self.assertEquals(n1.title, 'abc')

        n2 = g.BaseObject(title = 'abc')
        self.assertEquals(n2.title, 'abc')
        self.assertEquals(n1, n2)

        n1.sameas = n2
        self.assertEquals(n1.sameas, n2)

        n2.plot = 'empty'
        self.assertEquals(n1.sameas.title, 'abc')
        self.assertEquals(n1.sameas.plot, 'empty')

    def testBasicOntology(self):
        print 'b'
        class A(BaseObject):
            schema = { 'a': int  }
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

        self.assertEquals(issubclass(A, BaseObject), True)
        self.assertEquals(issubclass(B, A), True)
        self.assertEquals(issubclass(A, A), True)
        self.assertEquals(issubclass(A, B), False)
        self.assertEquals(issubclass(B, BaseObject), True)
        self.assertEquals(issubclass(C, A), False)
        self.assertEquals(B.parentClass().className(), 'A')

        OntologyManager.register(A, B, C)
        self.assertRaises(TypeError, OntologyManager.register, D)
        self.assertRaises(TypeError, OntologyManager.register, E)

        self.assert_(OntologyManager.getClass('A') is A)
        self.assertRaises(ValueError, OntologyManager.getClass, 'D')
        self.assert_(OntologyManager.getClass('B').parentClass().parentClass() is BaseObject)

        # test instance creation
        g = MemoryObjectGraph()
        a = g.A(title = 'Scrubs', epnum = 5)

        self.assertEquals(type(a), A)
        self.assertEquals(a.__class__, A)
        self.assertEquals(a.__class__.className(), 'A')
        self.assertEquals(a.__class__.__name__, 'A')

    def atestValidUniqueMethods(self):
        print 'c'
        class Episode(BaseObject):
            schema = { 'series': str,
                       'season': int,
                       'epnum': int,
                       'title': str
                       }

            unique = [ 'series', 'season', 'epnum' ]

        OntologyManager.register(Episode)

        g = MemoryObjectGraph()
        ep = g.Episode(series = 'House M.D.', season = 3, epnum = 2)
        #self.assertEquals(ep.isValid(), True) # construction of object should fail if not
        ep.title = 'gloub'
        ep.gulp = 'gloubiboulga'
        #self.assertEquals(ep.isValid(), True)
        self.assertRaises(TypeError, setattr, ep, 'title', 3)
        #self.assertEquals(ep.isValid(), False)

        self.assertEquals(ep.isUnique(), True)
        self.assertEquals(g.Episode(series='abc').isUnique(), False)

    def testBasicGraphBehavior(self):
        g = MemoryObjectGraph()
        print 'd'
        n1 = g.BaseObject(x = 1)
        print 'd1'
        n2 = g.BaseObject(x = 1)
        print 'd2'

        # graph belonging should be tested with identity
        g += n1
        self.assert_(n1 in g)
        self.assert_(n2 not in g)


    def atestReverseAttributeLookup(self):
        g = MemoryObjectGraph()
        print 'e'
        n1 = g.BaseObject(x = 1)
        n2 = g.BaseObject(x = 2, friend = n1)

        self.assertEquals(n2.friend, n1)
        self.assertRaises(AttributeError, getattr, n1, 'is_friend_of')

        g = ObjectGraph()
        g.addNode(n2) # this should also add n1 recursively
        self.assert_(n2 in g)
        self.assert_(n1 in g)
        self.assertEquals(n1.is_friend_of, n2)


    def atestFindObjectsInGraph(self):
        print 'f'
        # Ontology
        class Series(BaseObject):
            schema = { 'title': unicode,
                       'rating': float
                       }

            unique = [ 'title' ]

        class Episode(BaseObject):
            schema = { 'series': Series,
                       'season': int,
                       'episodeNumber': int,
                       'title': unicode,
                       'synopsis': unicode
                       }

            unique = [ 'series', 'season', 'episodeNumber' ]

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

        class Role(BaseObject):
            schema = { 'movie': Movie,
                       'actor': Person,
                       'character': Character
                       }

            schema = [ ('movie', Movie, 'roles'),
                       ('actor', Person, 'actingRoles'),
                       ('character', Character, 'roles')
                       ]

            # reverseLookup are used to indicated the name to be used for
            # the property name when following a relationship between objects in the other direction
            # ie: if Episode(...).series == Series('Scrubs'), then we define automatically
            # a way to access the Episode() from the pointed to Series() object.
            # with 'series' -> 'episodes', we then have:
            # Series('Scrubs').episodes = [ Episode(...), Episode(...) ]
            reverseLookup = { 'actor': 'role'
                               }

        g.findAll(type = Movie)
        g.findAll(Episode, lambda x: x.season == 2)
        g.findAll(Episode, season = 2)
        g.findall(Movie, lambda m: m.release_year > 2000)
        g.findAll(Person, role_movie_title = 'The Dark Knight') # role == Role.isPersonOf
        g.findAll(Character, isCharacterOf_movie_title = 'Fear and Loathing in Las Vegas', regexp = True)
        g.findAll(Character, is_character_of__movie__title = 'Fear and loathing.*', regexp = True)
        print c.isCharacterOf.movie.title
        print c.is_character_of.movie.title

    def testChainedAttributes(self):
        #a = findAll(Episode, series__title = 'Scrubs')
        pass

if __name__ == '__main__':
    unittest.main()
