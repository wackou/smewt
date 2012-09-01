<%inherit file="base_style.mako"/>


<%def name="make_episode_box(ep, displayStyle='inline')">

<%
from smewt.base.utils import tolist

filename = tolist(ep.get('files'))[0].get('filename')
title = '%s - %s' % (ep.get('episodeNumber', '?'),
                     ep.get('title', filename))
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


<%def name="make_media_box(f)">
<%
from smewt.base import SmewtUrl
%>
<div class="well">
  <a href="${SmewtUrl('action', 'play', {'filename1': f.filename })}">${f.filename}</a>

</div>

</%def>


${next.body()}
