<%inherit file="base_style.mako"/>

<%def name="make_subtitle_link(subtitle)">
  <%
  sublink = subtitle.subtitleLink()
  %>
  <a href="${sublink.url}"><img src="${sublink.languageImage}" /></a>
</%def>


<%def name="make_episode_box(ep, displayStyle='inline')">

<%
from smewt.base.utils import tolist

filename = tolist(ep.get('files'))[0].get('filename')
title = '%s - %s' % (ep.get('episodeNumber', '?'),
                     ep.get('title', filename))
%>
<div class="well">
  <div class="episode">
    <a href="${ep.playUrl()}">${title}</a>

    ## TODO: subtitleUrls
    %for subtitle in sorted(tolist(ep.get('subtitles')), key=lambda s: s.language):
      ${make_subtitle_link(subtitle)}
    %endfor

    %if 'synopsis' in ep:
      <div name="synopsis" style="display:${displayStyle}"><p>${ep.synopsis}</p></div>
    %endif
  </div>
</div>

</%def>


${next.body()}
