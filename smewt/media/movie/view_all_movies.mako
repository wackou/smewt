<%!
from smewt.base.smewturl import SmewtUrl
from smewt.base.mediaobject import Media
from smewt.base.utils import pathToUrl, smewtDirectoryUrl

import_dir = smewtDirectoryUrl('smewt', 'media', 'movie')
%>

<%
movies = sorted([ { 'title': m.title,
                    'url': SmewtUrl('media', 'movie/single', { 'title': m.title }),
                    'poster': pathToUrl(m.loresImage) } for m in context['movies'] ],
                    key = lambda x: x['title'])
%>

<html>
<head>
  <title>All movies view</title>
  <link rel="stylesheet" href="file://${import_dir}/movies.css">
</head>

<body>

<div id="wrapper">
    <div id="header">
        ALL MOVIES
    </div>
    <div id="container">

    %if movies:
      <div id="left-side">
      %for m in movies[::2]:
        <div class="movie">
          <img src="file://${m['poster']}" />
          <a href="${m['url']}">${m['title']}</a>
        </div>
      %endfor
      </div>

      <div id="right-side">
      %for m in movies[1::2]:
        <div class="movie">
          <img src="file://$m.poster" />
          <a href='${m.url}'>${m.title}</a>
        </div>
      %endfor
      </div>
    %else:
      <p>There are no movies in your library. Make sure you go into <b>Collection -> Select movies folders</b> to tell Smewt where to look for them.</p>
    %endif

  </div>
</div>

</body>
</html>
