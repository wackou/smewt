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

<%
from smewt import SMEWTD_INSTANCE
config = SMEWTD_INSTANCE.database.config
%>

<div class="container-fluid">
  <div class="row-fluid">

    <div class="span4"><div class="well">
      <a href="/movies">
      <!-- <img src="/user/speeddial/allmovies.png" width="200" /></a> -->
      <img src="/static/images/speeddial/media-optical-dvd-video.png" /></a>
      <p>Movies</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="/movies/table">
      <!-- <img src="/user/speeddial/moviestable.png" width="200" /></a> -->
      <img src="/static/images/speeddial/view-media-playlist.png" /></a>
      <p>Movie List</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="/movies/recent">
      <!-- <img src="/user/speeddial/recentmovies.png" width="200" /></a> -->
      <img src="/static/images/speeddial/folder-temp.png" /></a>
      <p>Recently Watched Movies</p>
    </div></div>

  </div>
  <div class="row-fluid">

    <div class="span4"><div class="well">
      <a href="/series">
      <!-- <img src="/user/speeddial/allseries.png" width="200" /></a> -->
      <img src="/static/images/speeddial/media-optical-video.png" /></a>
      <p>Series</p>
    </div></div>

    <div class="span4"><div class="well">
      <a href="/series/suggestions">
      <!-- <img src="/user/speeddial/episodesuggestions.png" width="200" /></a> -->
      <img src="/static/images/speeddial/favorites.png" /></a>
      <p>Episode Suggestions</p>
    </div></div>


    %if config.get('tvuMldonkeyPlugin'):
    <div class="span4"><div class="well">
      <a href="/feeds">
      <!-- <img src="/user/speeddial/feeds.png" width="200" /></a> -->
      <img src="/static/images/speeddial/network-wireless.png" /></a>
      <p>Feed Watcher</p>
    </div></div>
    %endif

    </div>
</div>
