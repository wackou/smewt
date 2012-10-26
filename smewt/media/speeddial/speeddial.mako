<%inherit file="base_style.mako"/>

<%block name="style">
${parent.style()}

<style type="text/css">

p {
    text-decoration: none;
    font: bold 20px Verdana, sans-serif;
    color: #448;
}

.well {
    background-color: #BBBBBB;
    text-align: center;
}

.well img {
    margin: 10px;
}

</style>
</%block>


<%!
from smewt.base.utils import smewtDirectoryUrl, smewtUserDirectoryUrl
smewt_dir = smewtDirectoryUrl('smewt', 'media', 'speeddial')
import_dir = smewtUserDirectoryUrl('speeddial')
%>

<div class="container-fluid">
  <div class="row-fluid">

    <div class="span4"><div class="well">
      <a href="smewt://media/movie">
      <img src="${import_dir}/allmovies.png" width="200" /></a>
      <p>Movies</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="smewt://media/movie/spreadsheet">
      <img src="${import_dir}/moviespreadsheet.png" width="200" /></a>
      <p>Movie List</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="smewt://media/movie/recent">
      <img src="${import_dir}/recentmovies.png" width="200" /></a>
      <p>Recently Watched Movies</p>
    </div></div>

  </div>
  <div class="row-fluid">

    <div class="span4"><div class="well">
      <a href="smewt://media/series">
      <img src="${import_dir}/allseries.png" width="200" /></a>
      <p>Series</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="smewt://media/series/suggestions">
      <img src="${import_dir}/episodesuggestions.png" width="200" /></a>
      <p>Episode Suggestions</p>
    </div></div>

    <!--
    <div class="span4"><div class="well">
      <a href="smewt://media/feeds">
      <img src="${import_dir}/feedwatcher_200x150.png" width="200" /></a>
      <p>Feed Watcher</p>
    </div></div>
    -->
    </div>
</div>
