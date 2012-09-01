<%inherit file="base_episode.mako"/>

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
extras = defaultdict(list)

# find episodes by season
for ep in [ ep for ep in tolist(series.episodes) if ep.get('episodeNumber', -1) > 0 ]:
    episodes[ep.season].append(ep)

for season, eps in episodes.items():
    episodes[season] = sorted(eps, key=lambda x:x.get('episodeNumber', 1000))

# find extras by season
for ep in [ ep for ep in tolist(series.episodes) if ep.get('episodeNumber', -1) <= 0 and ep.get('files') ]:
    for f in ep.files:
      extras[ep.season].append(f)


import os.path


lastSeasonWatched = series.get('lastSeasonWatched', 0)


%>


<%block name="scripts">
${parent.scripts()}

## for toggleByName. FIXME: could we not use jquery for that?
<script type="text/javascript" src="${import_dir}/3rdparty/styler.js"></script>

<script type="text/javascript">
// Select first tab by default
// TODO: should select the one for lastSeasonWatched
$('#seasontabs a:first').tab('show');

function toggleSynopsis() {
    toggleByName('synopsis');
    mainWidget.toggleSynopsis(isToggled('synopsis'));
}
</script>

</%block>


<%def name="make_subtitle_download_links(series)">
<%
englishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series, 'language': 'en' })
frenchSubsLink  = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series, 'language': 'fr' })
spanishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series, 'language': 'es' })
%>
    <div class="row-fluid">
      Subtitles:
      <div class="btn"><a href="${englishSubsLink}">Get missing English subtitles</a></div>
      <div class="btn"><a href="${frenchSubsLink}">Get missing French subtitles</a></div>
      <div class="btn"><a href="${spanishSubsLink}">Get missing Spanish subtitles</a></div>
      <br><br>
    </div>

</%def>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <img src="${poster}" height="130px" width:"auto"/>
    </div>
    <div class="span10">
      <br>
      Display: <div class="btn" onclick="toggleSynopsis()">Toggle synopsis</div>
    </div>
    <br><br><br>
    <div class="span10">
      ${make_subtitle_download_links(series)}
    </div>
  </div>

  <br>



<%def name="make_season_tab_header(tabid, season)">
    <li><a href="#tab${tabid}" data-toggle="tab">Season ${season}</a></li>
</%def>


<%def name="make_season_tab(tabid, series, season, eps, extras)">
    <div class="tab-pane" id="tab${tabid}">
      %for ep in eps:
      ${parent.make_episode_box(ep)}
      %endfor

      %if extras:
        <br>
        <h1>Extras / Untitled / Metadata unknown</h1>
        <br>
        %for f in extras:
          ${parent.make_media_box(f)}
        %endfor

      %endif

    </div>
</%def>


## TODO: activate tab for which seasonNumber == lastSeasonWatched:
<div class="tabbable"> <!-- Only required for left/right tabs -->
  <ul class="nav nav-tabs" id="seasontabs">
    <% seasons = sorted(set(episodes.keys()) | set(extras.keys())) %>
    %for season in seasons:
      ${make_season_tab_header(loop.index, season)}
    %endfor
  </ul>
  <div class="tab-content">
    %for season in seasons:
      ${make_season_tab(loop.index, series.title, season, episodes[season], extras[season])}
    %endfor
  </div>
</div>

</div>


############ FIXME: OLD STUFF STILL NOT PORTED

%if series.title == 'Unknown':

<%
files = []
for ep in tolist(series.get('episodes')):
    files += [ f.filename for f in tolist(ep.files) ]

unknownFiles = [ SDict({ 'title': f,
                         'url': SmewtUrl('action', 'play', { 'filename1': f })
                         })
                 for f in files ]

unknownFiles.sort(key = lambda f: f['title'])

%>

    %for ep in unknownFiles:
        <div class="episode"><a href="${ep.url}"><i>${ep.title}</i></a></div>
    %endfor

%endif
