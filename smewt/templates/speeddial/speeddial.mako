<%inherit file="smewt:templates/common/base_style.mako"/>

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
      <a href="/movies">
      <img src="/user/speeddial/allmovies.png" width="200" /></a>
      <p>Movies</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="/movies/table">
      <img src="/user/speeddial/moviespreadsheet.png" width="200" /></a>
      <p>Movie List</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="/movie/recent">
      <img src="/user/speeddial/recentmovies.png" width="200" /></a>
      <p>Recently Watched Movies</p>
    </div></div>

  </div>
  <div class="row-fluid">

    <div class="span4"><div class="well">
      <a href="/series">
      <img src="/user/speeddial/allseries.png" width="200" /></a>
      <p>Series</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="/series/suggestions">
      <img src="/user/speeddial/episodesuggestions.png" width="200" /></a>
      <p>Episode Suggestions</p>
    </div></div>

    <!--
    <div class="span4"><div class="well">
      <a href="/feeds">
      <img src="/user/speeddial/feedwatcher_200x150.png" width="200" /></a>
      <p>Feed Watcher</p>
    </div></div>
    -->
    </div>
</div>
