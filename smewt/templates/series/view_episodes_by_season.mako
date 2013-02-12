<%inherit file="smewt:templates/series/base_episode.mako"/>

<%!
from collections import defaultdict
from smewt import SmewtUrl
from smewt.ontology import Episode, Series, Subtitle
from smewt.base.utils import pathToUrl, smewtMediaUrl, tolist, SDict
from smewt.base import SmewtException
from guessit.language import ALL_LANGUAGES
import os.path
import guessit

%>

<%
series = context['series']

poster = '/user/images/' + series.get('hiresImage').split('/')[-1]

# First prepare the episodes, grouping them by season
episodes = defaultdict(list)
extras = defaultdict(list)

# find episodes by season
for ep in [ ep for ep in tolist(series.episodes) if ep.get('episodeNumber', -1) > 0 ]:
    epfiles = ep.get('files')
    if not epfiles:
        continue
    episodes[ep.season].append(ep)

for season, eps in episodes.items():
    episodes[season] = sorted(eps, key=lambda x:x.get('episodeNumber', 1000))

# find extras by season
for ep in [ ep for ep in tolist(series.episodes) if ep.get('episodeNumber', -1) <= 0 and ep.get('files') ]:
    for f in tolist(ep.files):
        extras[ep.season].append(f)


lastSeasonWatched = series.get('lastSeasonWatched', 0)

%>


<%block name="scripts">
${parent.scripts()}

## for toggleByName. FIXME: could we not use jquery for that?
<script type="text/javascript" src="/static/js/styler.js"></script>

<script type="text/javascript">
// Select first tab by default
// TODO: should select the one for lastSeasonWatched
$('#seasontabs a:first').tab('show');

function toggleSynopsis() {
    toggleByName('synopsis');

    $.post('/config/set/displaySynopsis',
           { value: isToggled('synopsis') });
}

</script>

</%block>


<%def name="make_subtitle_download_links(series)">
<%
subsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': series })
%>

 <div class="row-fluid">

   Look for subtitles in
   ${parent.make_lang_selector(context['smewtd'])}

   <div class="btn"><a href="${subsLink}">Download!</a></div>
   <br><br>
 </div>

</%def>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <img src="${poster}" height="130px" width:"auto"/>
    </div>
%if series.title != 'Unknown':
    <div class="span10">
      <br>
      Display: <div class="btn" onclick="toggleSynopsis()">Toggle synopsis</div>
    </div>
    <br><br><br>
    <div class="span10">
      ${make_subtitle_download_links(series.title)}
    </div>
%endif
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


%if series.title != 'Unknown':

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

%else: ## series.title == 'Unknown'

<div class="tabbable"> <!-- Only required for left/right tabs -->
  <ul class="nav nav-tabs" id="seasontabs">
    ${make_season_tab_header(0, '??')}
  </ul>
  <div class="tab-content">
    <%
    files = []
    for ep in tolist(series.get('episodes')):
        for f in tolist(ep.files):
            files.append(f)
    files = sorted(files, key=lambda f: f.filename)
    %>
    %for f in files:
        ${parent.make_media_box(f)}
    %endfor
  </div>
</div>

%endif

</div>
