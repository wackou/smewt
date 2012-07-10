<%inherit file="base_list_view.mako"/>

<%!
from smewt import SmewtUrl
from smewt.base.utils import SDict, pathToUrl

%>

<%
movies = sorted([ SDict(title = m.title,
                        url = SmewtUrl('media', 'movie/single', { 'title': m.title }),
                        poster = pathToUrl(m.loresImage))
                  for m in context['movies'] ],
                key = lambda x: x.title)
%>

<%block name="list_header">
  ALL MOVIES
</%block>


%if movies:

  ${parent.make_title_list(movies)}

%else:

  <p>There are no movies in your library. Make sure you go into <b>Collection -> Select movies folders</b> to tell Smewt where to look for them.</p>

%endif
