# the following query is not correct, as the role could be different in the role__character and
# the role__movie__title unless we make it that when having multiple properties starting with the same node
# it should be the same (more natural, but implementation is harder)
# a workaround solution would be to do findOne(Role, character = 'Indiana', ...).actor
findOne(Actor,
        role__character = 'Indiana',
	role__movie__title, '.*Indiana Jones.*',
        regexp = True)



in fact, we have "dynamic polymorphism" in the sense that our nodes in the graph can be attributed
a class at runtime depending on the properties they have. If there is a match, the node is considered
a valid object and is treated as a correctfully constructed object. It's as if we had "dynamic interfaces"
that we would map onto objects at runtime, only extracting the needed information from the nodes
in the way most useful to us.



a query is a tree that needs to be mapped on top of the graph. the property names indicated the
direction in which to follow the nodes to recurse down the tree (it is pattern matching of
a (directed) tree on an undirected graph whose links have a different name depending on the
direction they are traversed)
 

----------------------------------------------------

when registering the classes, we need to make sure that between all the reverse lookups, there are no ambiguities.
ie: the following should be illegal:

class A:
  schema = { 'b': B }
  reverseLookup = { 'b': 'a' }

class A2:
  schema = { 'b2': B }
  reverseLookup = { 'b2': 'a' }

because then we cannot know whether B.a is a A or a A2
