<%inherit file="smewt:templates/movie/base_movie.mako"/>

<%!
from collections import defaultdict
from smewt.ontology import Movie
from smewt.base.utils import tolist
from smewt.base import SmewtException
import os
import urllib

%>


<%block name="scripts">
${parent.scripts()}

<script type="text/javascript">
// Select last viewed tab
$("#movietabs li:eq(${movie.get('lastViewedTab', 0)}) a").tab("show");

$('#movietabs a').click(function (e) {
    e.preventDefault();
    $(this).tab('show');
    var url = e.target.href.split('#');
    var tab = url[url.length-1].slice(3);
    action("set_last_viewed_tab", {title: '${self.attr.SQ(movie.title) | n}', 'tab': tab});
})

function playMovie(title, language) {
    action("play_movie", { title: title, sublang: language });
}


</script>

</%block>


<%def name="make_subtitle_download_links(movie)">

Look for subtitles in
${parent.make_lang_selector(context['smewtd'])}

<div class="btn" onclick="getSubtitles('movie', '${self.attr.Q_sq(movie.title)}')">Download!</div>

</%def>

<div class="container-fluid">
  <div class="row-fluid">
    <div class="span2">
      <img src="${movie.hiresImage}" height="250px;" width="auto"/>
    </div>
%if movie.title != 'Unknown':
    <div class="span10">
      <br>
      Movie:
      <div class="btn" onclick="playMovie('${self.attr.Q_sq(movie.title)}');"> <i class="icon-play"></i> </div>

      %for subtitle in sorted(tolist(movie.get('subtitles')), key=lambda s: s.language):
        <div class="btn" onclick="playMovie('${self.attr.Q_sq(movie.title)}', '${subtitle.language}');">
          <img src="${subtitle.languageFlagLink()}" />
        </div>
      %endfor

    </div>
%else:
<br><br>
%endif

    <div class="span10">
      <br>
        ${parent.video_control()}
    </div>

%if movie.title != 'Unknown':
    <div class="span10">
      <br>
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

<div class="tabbable">

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
