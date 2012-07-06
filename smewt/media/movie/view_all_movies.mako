<%inherit file="base_list_view.mako"/>

<%!
from smewt.base.smewturl import SmewtUrl
from smewt.base.utils import pathToUrl

class SDict(dict):
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except AttributeError:
            return self[attr]

%>

<%
movies = sorted([ SDict(title = m.title,
                        url = SmewtUrl('media', 'movie/single', { 'title': m.title }),
                        poster = pathToUrl(m.loresImage))
                  for m in context['movies'] ],
                key = lambda x: x.title)
%>


<div class="container-fluid">
  <div id="header">
    ALL MOVIES
  </div>


%if movies:

  <%namespace name="listview" file="base_list_view.mako"/>

  ${listview.wells_list(movies)}

%else:

  <p>There are no movies in your library. Make sure you go into <b>Collection -> Select movies folders</b> to tell Smewt where to look for them.</p>

%endif

</div>
