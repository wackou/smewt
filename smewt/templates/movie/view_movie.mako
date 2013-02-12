<%inherit file="smewt:templates/movie/base_movie.mako"/>

<%!
from collections import defaultdict
from smewt import SmewtUrl
from smewt.ontology import Movie
from smewt.base.utils import pathToUrl, smewtMediaUrl, tolist
from smewt.base import SmewtException
import os
import urllib

import_dir = smewtMediaUrl()

%>


<%block name="scripts">
${parent.scripts()}

<script type="text/javascript">
// Select first tab by default
// TODO: should select the one for lastSeasonWatched
$('#movietabs a:first').tab('show');

function playMovie(title, language) {
    action("play_movie", { title: title, sublang: language });
}

function getSubtitles(type, title) {
    action("get_subtitles", { type: type, title: title });
}

</script>

</%block>


<%def name="make_subtitle_download_links(movie)">

Look for subtitles in
${parent.make_lang_selector(context['smewtd'])}

<div class="btn" onclick="getSubtitles('movie', '${urllib.quote(movie.title)}')">Download!</div>

</%def>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <img src="${movie.loresImage}" height="130px" width="auto"/>
    </div>
%if movie.title != 'Unknown':
    <div class="span10">
      <br>
      Movie:
      <div class="btn" onclick="playMovie('${urllib.quote(movie.title)}');">Play</div>

      %for subtitle in sorted(tolist(movie.get('subtitles')), key=lambda s: s.language):
        <div class="btn" onclick="playMovie('${urllib.quote(movie.title)}', '${subtitle.language}');">
          <img src="${subtitle.languageFlagLink()}" />
        </div>
      %endfor

    </div>
    <br><br><br>
    <div class="span10">
      ${make_subtitle_download_links(movie)}
    </div>
%endif
  </div>

  <br>


%if movie.title == 'Unknown':
  <p>&nbsp;</p>

  %for f in tolist(movie.get('files')):
    ${parent.make_media_box(f)}
  %endfor


%else:

<div class="tabbable"> <!-- Only required for left/right tabs -->

  <ul class="nav nav-tabs" id="movietabs">
    <li><a href="#tab0" data-toggle="tab">Overview</a></li>
    <li><a href="#tab1" data-toggle="tab">Cast</a></li>
    <li><a href="#tab2" data-toggle="tab">Comments</a></li>
    <li><a href="#tab3" data-toggle="tab">Files</a></li>
  </ul>

  <div class="tab-content">
    <div class="tab-pane" id="tab0">
      ${parent.make_movie_overview(movie)}
    </div>
    <div class="tab-pane" id="tab1">
      ${parent.make_movie_cast(movie)}
    </div>
    <div class="tab-pane" id="tab2">
      ${parent.make_movie_comments(movie)}
    </div>
    <div class="tab-pane" id="tab3">
      ${parent.make_movie_files(movie)}
    </div>

  </div>
</div>
%endif
