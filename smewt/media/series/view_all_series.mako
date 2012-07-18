<%inherit file="base_list_view.mako"/>

<%!
from smewt import SmewtUrl
from smewt.base.utils import SDict, pathToUrl

%>

<%
series = sorted([ SDict(title = s.title,
                        url = SmewtUrl('media', 'series/single', { 'title': s.title }),
                        poster = pathToUrl(s.loresImage))
                  for s in context['series'] ],
                key = lambda x: x.title)
%>


%if series:

  ${parent.make_title_list(series)}

%else:

  <p>There are no episodes in your library. Make sure you go into <b>Collection -> Select series folders</b> to tell Smewt where to look for them.</p>

%endif
