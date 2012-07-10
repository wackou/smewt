<%inherit file="base.mako"/>

<%!
from itertools import groupby
from collections import defaultdict
from smewt import SmewtUrl, Media
from smewt.media import Episode, Series, Subtitle
from smewt.base.utils import pathToUrl, smewtMediaUrl, tolist, SDict
from smewt.base import SmewtException
from smewt.base.actionfactory import PlayAction
import guessit

import_dir = smewtMediaUrl()
flags_dir = smewtMediaUrl('common', 'images', 'flags')

%>

<%
series = context['series']
displaySynopsis = context['displaySynopsis']

poster = pathToUrl(series.get('hiresImage'))
if displaySynopsis:
    displayStyle = 'inline'
else:
    displayStyle = 'none'

# First prepare the episodes, grouping them by season
episodes = defaultdict(list)
for ep in tolist(series.episodes):
   episodes[ep.season].append(ep)

for season, eps in episodes.items():
   episodes[season] = sorted(eps, key=lambda x:x.get('episodeNumber', 1000))


import os.path


lastSeasonWatched = series.get('lastSeasonWatched', 0)


%>


<%block name="scripts">

## for toggleByName
<script type="text/javascript" src="${import_dir}/3rdparty/styler.js"></script>

<script type="text/javascript">
// Select first tab by default
// TODO: should select the one for lastSeasonWatched
$(function() { $('#seasontabs a:first').tab('show'); });

function toggleSynopsis() {
    toggleByName('synopsis');
    mainWidget.toggleSynopsis(isToggled('synopsis'));
}
</script>

</%block>

<style>
.well {
 padding: 10px;
 margin-bottom: 10px;
}
</style>

<div class="container-fluid">

  <div class="row-fluid">
    <div class="span2">
      <img src="${poster}" height="130px" width:"auto"/>
    </div>
    <div class="span10">
      <h1>${series.title}</h1>
      <div class="btn" onclick="toggleSynopsis()">Toggle synopsis</div>
    </div>
  </div>

  <br>

<%def name="make_subtitle_link(subtitle)">
  <%
  sublink = subtitle.subtitleLink()
  %>
  <a href="${sublink.url}"><img src="${sublink.languageImage}" /></a>
</%def>

<%def name="make_episode(ep)">
<div class="well">
      <div class="episode">
        <a href="${ep.playUrl()}">${ep.get('episodeNumber', '?')} -
          ${ep.get('title', tolist(ep.get('files'))[0].get('filename'))} </a>

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

<%def name="make_season_tab_header(tabid, season, active=False)">
    <li${' class="active"' if active else ''}><a href="#tab${tabid}" data-toggle="tab">Season ${season}</a></li>
</%def>


<%def name="make_subtitle_download_links(series, season)">
<%
englishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series, 'season': season, 'language': 'en' })
frenchSubsLink  = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series, 'season': season, 'language': 'fr' })
spanishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series, 'season': season, 'language': 'es' })
%>
    <div class="row-fluid">
      <div class="btn"><a href="${englishSubsLink}">Get missing English subtitles</a></div>
      <div class="btn"><a href="${frenchSubsLink}">Get missing French subtitles</a></div>
      <div class="btn"><a href="${spanishSubsLink}">Get missing Spanish subtitles</a></div>
      <br><br>
    </div>

</%def>

<%def name="make_season_tab(tabid, series, season, eps)">
    <div class="tab-pane" id="tab${tabid}">
      ${make_subtitle_download_links(series, season)}

      %for ep in eps:
      ${make_episode(ep)}
      %endfor
    </div>
</%def>

## $('#myTab a:first').tab('show'); // Select first tab


## TODO: activate tab for which seasonNumber == lastSeasonWatched:
<div class="tabbable"> <!-- Only required for left/right tabs -->
  <ul class="nav nav-tabs" id="seasontabs">
    %for season, eps in episodes.items():
    ${make_season_tab_header(loop.index, season)}
    %endfor
  </ul>
  <div class="tab-content">
    %for season, eps in episodes.items():
    ${make_season_tab(loop.index, series.title, season, eps)}
    %endfor
  </div>
</div>

</div>


############ OLD STUFF STILL NOT PORTED

%if series.title != 'Unknown':


### Unknown episodes

<%
import os.path
eps = [ ep for ep in tolist(series.get('episodes')) if ep.episodeNumber == -1 and ep.get('files') ]

files = []
for ep in eps:
    files += [ f.filename for f in tolist(ep.files) ]

extras = [ { 'title': f,
             'url': SmewtUrl('action', 'play', { 'filename1': f })
             }
             for f in files ]
%>

  %if extras:
    <div class="extras">Extras / Untitled / Metadata unknown</div>
  %endif
  %for ep in extras:
    <div class="episode"><a href="${ep.url}"><i>${ep.title}</i></a></div>
  %endfor


%else:
<!-- series == unknown -->

<%
files = []
for ep in tolist(series.get('episodes')):
    files += [ f.filename for f in tolist(ep.files) ]

unknownFiles = [ { 'title': f,
                   'url': SmewtUrl('action', 'play', { 'filename1': f })
                   }
                   for f in files ]

unknownFiles.sort(key = lambda f: f['title'])

%>

    %for ep in unknownFiles:
        <div class="episode"><a href="${ep.url}"><i>${ep.title}</i></a></div>
    %endfor

%endif
