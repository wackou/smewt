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



in neo4j:
 - nodes are persistent, hence always live in a graph (ie: they can't be free, unbound to a graph)
 - the ontology is defined inside the graph as well (for indexing by class)



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
  # WARNING: This is outdated, Nodes always need to be used through a BaseObject interface to be able to access those methods
  - look into the valid classes this node has for a corresponding method
    -> the order here is important: if all possible classes are part of the same hierarchy,
       just take the most derived class and call its method: "all functions are virtual"
    -> if they are part of 2 different hierarchies, no guarantee is made as to which function is called
       however, if we want to guarantee the execution of a specific class's method, we can do it with
       MyClass(node).somefunc instead of node.somefunc
       (note no parentheses are used, the function is always called without any arguments)




a query is a tree that needs to be mapped on top of the graph. the property names indicated the
direction in which to follow the nodes to recurse down the tree (it is pattern matching of
a (directed) tree on an undirected graph whose links have a different name depending on the
direction they are traversed)
 

----------------------------------------------------

even though all declared properties in a schema need to have an associated reverse lookup name, we still need to have the is_*_of relation searched, because we might use and set properties which are not part of the schema, in which case they still need to be accessible in both directions.

when registering the classes, we need to make sure that between all the reverse lookups, there are no ambiguities.
ie: the following should be illegal:

class A:
  schema = { 'b': B }
  reverseLookup = { 'b': 'a' }

class A2:
  schema = { 'b2': B }
  reverseLookup = { 'b2': 'a' }

because then we cannot know whether B.a is a A or a A2
