<%inherit file="base_movie.mako"/>

<%!
from collections import defaultdict
from smewt import SmewtUrl, Media
from smewt.media import Movie
from smewt.base.utils import pathToUrl, smewtDirectoryUrl, tolist
from smewt.base import SmewtException
import os

import_dir = smewtDirectoryUrl('smewt', 'media')
flags_dir = smewtDirectoryUrl('smewt', 'media', 'common', 'images', 'flags')
%>

<%
poster = pathToUrl(movie.loresImage)
%>

<%def name="make_subtitle_download_links(movie)">
<%
englishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'movie', 'title': movie.title, 'language': 'en' })
frenchSubsLink  = SmewtUrl('action', 'getsubtitles', { 'type': 'movie', 'title': movie.title, 'language': 'fr' })
spanishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'movie', 'title': movie.title, 'language': 'es' })
%>
    <div class="row-fluid">
      Subtitles:
      <div class="btn"><a href="${englishSubsLink}">Get missing English subtitles</a></div>
      <div class="btn"><a href="${frenchSubsLink}">Get missing French subtitles</a></div>
      <div class="btn"><a href="${spanishSubsLink}">Get missing Spanish subtitles</a></div>

    </div>
</%def>


<%block name="scripts">
${parent.scripts()}

<script type="text/javascript">
// Select first tab by default
// TODO: should select the one for lastSeasonWatched
$('#movietabs a:first').tab('show');

</script>

</%block>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <img src="${poster}" height="130px" width:"auto"/>
    </div>
%if movie.title != 'Unknown':
    <div class="span10">
      <br>
      Movie:
      <div class="btn"><a href="${movie.playUrl()}">Play</a></div>

      %for subtitle in sorted(tolist(movie.get('subtitles')), key=lambda s: s.language):
        <div class="btn">${parent.make_subtitle_link(subtitle)}</div>
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
