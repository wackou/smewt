from Cheetah.Template import Template

HTML_SERIES = '''<html>
<head>
  <title>cheetah test</title>
</head>

<body>
#for $serie, $eps in $series.items()
  <h1>$serie</h1>
  #for $ep in $eps
    <div class="episode">$ep.epnumber - $ep.title</div>
  #end for
#end for

</body>
</html>
'''


def render(eps):
    series = {}
    for ep in eps:
        try:
            series[ep['serie']].append(ep)
        except:
            series[ep['serie']] = [ ep ]

    html = open('series/template.html').read()
    t = Template(html, searchList = { 'series': series })

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


