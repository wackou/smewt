from Cheetah.Template import Template


# all the logic of rendering should be contained in the template
# we shall always pass only a list of the basic media object
# (eg for series, we have SerieObject, EpisodeObject, SeasonObject...
#  but the base type is EpisodeObject (a single file)
#  That means that if the view should represent a list of all
#  the series available, it needs to do its groupby by itself)
def render(episodes):
    print '---- Rendering episode:', episodes

    t = Template(file = 'media/series/view_episodes_by_season.tmpl',
                 searchList = { 'episodes': episodes })

    return unicode(t)



def cheetahTest():
    eps = [ { 'filename': 'file:///data/blah/01.avi',
              'serie': 'Black Lagoon',
              'season': 1,
              'epnumber': 1,
              'title': 'Black Lagoon'
              },
            { 'filename': 'file:///data/blah/02.avi',
              'serie': 'Black Lagoon',
              'season': 1,
              'epnumber': 2,
              'title': 'Heavenly Gardens'
              },
            { 'filename': 'file:///data/blouh/01.avi',
              'serie': 'Noir',
              'season': 1,
              'epnumber': 1,
              'title': 'La vierge aux mains noires'
              }
            ]

    return render(eps)


