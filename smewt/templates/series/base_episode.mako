<%inherit file="smewt:templates/common/base_style.mako"/>


<%def name="make_episode_box(ep, displayStyle='inline')">

<%
from smewt.base.utils import tolist

filename = tolist(ep.get('files'))[0].get('filename')
title = '%s - %s' % (ep.get('episodeNumber', '?'),
                     ep.get('title', filename))

displaySynopsis = context.get('displaySynopsis', True)
if displaySynopsis:
    displayStyle = 'inline'
else:
    displayStyle = 'none'

%>
<div class="well">
  <a href="${ep.playUrl()}">${title}</a>

  %for subtitle in sorted(tolist(ep.get('subtitles')), key=lambda s: s.language):
    ${parent.make_subtitle_link(subtitle)}
  %endfor

  %if 'synopsis' in ep:
    <div name="synopsis" style="display:${displayStyle}"><p>${ep.synopsis}</p></div>
  %endif
</div>

</%def>


${next.body()}
