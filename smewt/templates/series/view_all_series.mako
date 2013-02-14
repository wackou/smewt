<%inherit file="smewt:templates/common/base_list_view.mako"/>

<%!
from smewt.base.utils import SDict
%>

<%
series = sorted([ SDict(title = s.title,
                        url = '/series/%s' % s.title,
                        poster = '/user/images/' + s.loresImage.split('/')[-1])
                  for s in context['series'] ],
                key = lambda x: x.title)
%>


%if series:

  ${parent.make_title_list(series)}

%else:

<p>There are no episodes in your library. Make sure you go into <b>Preferences</b>
and select one or more folders for your <b>series collection</b>,
then proceed to the <b>Control panel</b> and <b>update your collection</b>.
</p>

<p>
Your series should start appearing here shortly after!
</p>

%endif
