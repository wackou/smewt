in the graph object model, we can define a weaker inheritance, where classes are more like tags, even though we can order some of them as inheritance tree
that makes it possible for an object to have multiple classes even though, they are not part of the same tree, like as if the Director class doesn't inherit from the Person class

findAll(type = None, # look only for resources of a certain type. considerably speed up object lookup
        cond = None, # function that returns whether a given node should be selected
        **kwargs)    # attribute which should be equal to certain values. Can be chained django-style with __

the type lookup should also look for derived class
the cond might be optimized by first calling it on a proxy object which would detect which attributes (hence links in the graph) should be traversed
kwargs might be chained such as movie__director__lastName = 'Kubrick'

Example queries:
----------------

findAll(type = Movie)
findAll(cond = lambda x: x.season == 2, type = Episode)

findAll(cond = lambda movie: movie.title.director.name == 'X, Y')
findAll(Movie, title__director__name = 'X, Y')

bestMovies = [ movie for movie in find(Director, last_name = 'Kubrick').is_director_of
                 if movie.imdb_rating > 8.0 ],


findOne(Actor,
        role__character = 'Indiana',
	cond = lambda person: simpleSearch(person.role.movie.title, '.*Indiana Jones.*')

# the following query is not correct, as the role could be different in the role__character and
# the role__movie__title unless we make it that when having multiple properties starting with the same node
# it should be the same (more natural, but implementation is harder)
# a workaround solution would be to do findOne(Role, character = 'Indiana', ...).actor
findOne(Actor,
        role__character = 'Indiana',
	role__movie__title, '.*Indiana Jones.*',
        regexp = True)



define reverse attribute name definition (django yeah!)

ie: person.is_person_of (role) -> person.role

in neo4j:
 - nodes are persistent, hence always live in a graph (ie: they can't be free, unbound to a graph)
 - the ontology is defined inside the graph as well (for indexing by class)

creating a PersistentObjectNode *REQUIRES* a PersistentGraph (context)
-> should we allow it to be implicit? (nodes are automatically created in the default graph (a singleton))
-> the function addNode is a no-op (not if the node is not a PersistentObjectNode, but a simple ObjectNode)


when creating non-persistent ObjectNode, they do not need to be in a graph
it also probably doesn't make sense to put them in a default graph, because we might want
to create easily nodes that live in different graphs


adding a memObjectNode to a Neo4jObjectGraph should be possible (and thus make a deepcopy of the object)

in fact, we have "dynamic polymorphism" in the sense that our nodes in the graph can be attributed
a class at runtime depending on the properties they have. If there is a match, the node is considered
a valid object and is treated as a correctfully constructed object. It's as if we had "dynamic interfaces"
that we would map onto objects at runtime, only extracting the needed information from the nodes
in the way most useful to us.



attribute setting should be strict, it should only allow of the type declared.
ie, it accepted the role of using a node given some properties, it should not change their type
but only their value, so as to leave it in a usable state for later use, maybe by different
classes / interfaces

each time a new class is registered, we need to revalidate all objects.
-> registering the ontology should be done by the graph

each time a new node is created, it is checked against registered classes for validity, and
labelled as a correct instance if there's a match



----------------
if there are multiple interfaces that match a given node, we need to find a way to have a
correctly defined MRO for member methods propagation to the ObjectNode's __getattr__ method.

------------
Scenario:
- You have an undirected graph. It is the world
- You create nodes in your graph. Nodes are pure data: they can have any number of attributes
  of simple types: unicode, int, float, datetime, etc... and can also be linked together.
- A link is also considered as a property of a node, where a node is the parent and the other
  a child, the direction of the link determines the name of the property, ie: movie1.director == X
  -> X.filmography == [ movie1, movie2 ]
- There can be any number of links between nodes, even multiple links between 2 nodes, given that
  they have a different name
- when calling attributes on an ObjectNode, the following is resolved:
  - first look at an ObjectNode's attributes
  - look into the properties first
  - look into the valid classes this node has for a corresponding method
    -> the order here is important: if all possible classes are part of the same hierarchy,
       just take the most derived class and call its method: "all functions are virtual"
    -> if they are part of 2 different hierarchies, no guarantee is made as to which function is called
       however, if we want to guarantee the execution of a specific class's method, we can do it with
       MyClass(node).somefunc instead of node.somefunc
       (note no parentheses are used, the function is always called without any arguments)


there should not be ambiguity when calling member methods whose type can be deduced, ie:
if Episode.series -> Series, Series.func and Gloub.func are 2 functions that resolved
(series is a valid Series and a valid Gloub), then Episode.series.func should resolve to
the correct function Series.func


# This class allows to have correct MRO when chaining
class ObjectNodeInstance:
   def __init__(self):
      self._class = BaseObject
      self._node = ObjectNode

  def __getattr__(self, name):
      # TODO: do we want to have virtual functions?
      result = self._node.__getattr__(name, currentClass = self._class)
      # result is an ObjectNode
      return ObjectNodeInstance(self._class.schema[name], result)

we need to have member methods who accept a currentClass arg, which is the
current class of the object.

def BaseObject.__init__(self, copy = None):
    if


a query is a tree that needs to be mapped on top of the graph. the property names indicated the
direction in which to follow the nodes to recurse down the tree (it is pattern matching of
a (directed) tree on an undirected graph whose links have a different name depending on the
direction they are traversed)
 

----------------------------------------------------

Ontology depends on ObjectNode for BaseObject.__new__
ObjectNode._classes should not contain BaseObject 

even though all declared properties in a schema need to have an associated reverse lookup name, we still need to have the is_*_of relation searched, because we might use and set properties which are not part of the schema, in which case they still need to be accessible in both directions.

when registering the classes, we need to make sure that between all the reverse lookups, there are no ambiguities.
ie: the following should be illegal:


class A:
  schema = [ ('b', B, 'a')

class A2
  schema = [ ('b2', B, 'a')

because then we cannot know whether B.a is a A or a A2
