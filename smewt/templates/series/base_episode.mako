<%inherit file="smewt:templates/common/base_style.mako"/>
<%!
import urllib
%>

<%block name="scripts">
${parent.scripts()}

<script type="text/javascript">
function playEpisode(series, season, episodeNumber, sublang) {
    action("play_episode", { series: series, season: season,
                             episodeNumber: episodeNumber, sublang: sublang });
}
</script>

</%block>


<%def name="make_episode_box(ep, displayStyle='inline')">
<%
from smewt.base.utils import tolist

filename = tolist(ep.get('files'))[0].get('filename')
title = '%s - %s' % (ep.get('episodeNumber', '?'),
                     ep.get('title', filename))

if context['smewtd'].database.config.get('displaySynopsis', True):
    displayStyle = 'inline'
else:
    displayStyle = 'none'
%>

<div class="well">
  <a href="javascript:void(0);"
          onclick="playEpisode('${urllib.quote(ep.series.title)}', ${ep.season}, ${ep.episodeNumber});">${title}</a>

  %for subtitle in sorted(tolist(ep.get('subtitles')), key=lambda s: s.language):
    <img src="${subtitle.languageFlagLink()}"
         onclick="playEpisode('${urllib.quote(ep.series.title)}', ${ep.season}, ${ep.episodeNumber}, '${subtitle.language}');" />
  %endfor

  %if 'synopsis' in ep:
    <div name="synopsis" style="display:${displayStyle}"><p>${ep.synopsis}</p></div>
  %endif
</div>

</%def>

${next.body()}
