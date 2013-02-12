<%inherit file="smewt:templates/common/base_list_view.mako"/>

<%!
from smewt import SmewtUrl
from smewt.base.utils import SDict, pathToUrl

%>

<%

def posterUrl(p):
    if p.endswith('noposter.png'):
        return '/static/images/noposter.png'
    return '/user/images/' + p.split('/')[-1]

movies = sorted([ SDict(title = m.title,
                        url = '/movie/%s' % m.title,
                        #poster = posterUrl(m.loresImage))
                        poster = m.loresImage)
                  for m in context['movies'] ],
                key = lambda x: x.title)
%>

%if movies:

  ${parent.make_title_list(movies)}

%else:

<p>There are no movies in your library. Make sure you go into <b>Preferences</b>
and select one or more folders for your <b>movie collection</b>,
then proceed to the <b>Control panel</b> and <b>update your collection</b>.
</p>

<p>
Your movies should start appearing here shortly after!
</p>

%endif
