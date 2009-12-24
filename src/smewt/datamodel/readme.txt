in the graph object model, we can define a weaker inheritance, where classes are more like tags, even though we can order some of them as inheritance tree
that makes it possible for an object to have multiple classes even though, they are not part of the same tree, like as if the Director class doesn't inherit from the Person class

findAll(type = None, # look only for resources of a certain type. considerably speed up object lookup
        cond = None, # function that returns whether a given node should be selected
        **kwargs)    # attribute which should be equal to certain values. Can be chained django-style with __

the type lookup should also look for derived class
the cond might be optimized by first calling it on a proxy object which would detect which attributes (hence links in the graph) should be traversed
kwargs might be chained such as movie__director__lastName = 'Kubrick'



findAll(type = Movie)
findAll(cond = lambda x: x.season == 2, type = Episode)

findAll(cond = lambda movie: movie.title.director.name == 'X, Y')
findAll(Movie, title__director__name = 'X, Y')

bestMovies = [ movie for movie in find(Director, last_name = 'Kubrick').is_director_of
                 if movie.imdb_rating > 8.0 ],


findOne(Actor,
        role__character = 'Indiana',
	cond = lambda person: simpleSearch(person.role.movie.title, '.*Indiana Jones.*')


