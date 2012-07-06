<%!
from smewt import SmewtUrl
from smewt.base.utils import tolist, pathToUrl
from smewt.base.textutils import toUtf8
from itertools import groupby
import datetime
%>

<%
episodes = context['episodes']

# map of series to list of episodes
suggest = {}

episodeCount = 3

# first find the last viewed episode for each season
episodes = sorted(episodes, key = lambda ep: ep.series.title)

for serieName, eps in groupby(episodes, lambda ep: ep.series.title):
    eps = list(eps)
    lastViewed = max(eps, key = lambda ep: ep.lastViewed)


    # then look if we have a more recent one which we haven't watched yet
    s = []
    for ep in lastViewed.series.episodes:
        if 'title' in ep and (ep.season, ep.episodeNumber) >= (lastViewed.season, lastViewed.episodeNumber):
            s.append(ep)

    # find only more recent episode to watch
    if s:
        keep = sorted(s, key = lambda ep: (ep.season, ep.episodeNumber))[:episodeCount]
        suggest[keep[0].series] = keep

# sort our suggestions to show the last scanned ones first
suggest = sorted(suggest.items(), key = lambda eps: -tolist(eps[1][0].files)[0].lastModified)

from smewt.base.utils import smewtDirectoryUrl
import_dir = smewtDirectoryUrl('smewt', 'media')

%>

<html>
<head>
  <title>Episodes suggestions</title>
  <link rel="stylesheet" href="${import_dir}/series/series.css">
</head>

<body>

<div id="wrapper">
    <div id="header">
        EPISODES SUGGESTIONS
    </div>
    <div id="container">

    <div id="center-side">

    %if suggest:
      %for s, eps in suggest:
        <div class="series">
          <%
            url = SmewtUrl('media', 'series/single', { 'title': s.title })
            poster = pathToUrl(s.get('loresImage'))
          %>
          <img src="${poster}" />
          <a href='${url}'>${s.title}</a>
        </div>

        %for ep in eps:
        <div class="suggest">
          <% url = SmewtUrl('action', 'play', { 'filename1': tolist(ep.files)[0].filename }) %>
          %if 'title' in ep:
            <a href="${url}">${ep.episodeNumber} - ${ep.title} </a>
          %else:
            <a href="${url}">${ep.episodeNumber} - <i>Unknown</i> </a>
          %endif
            %if 'synopsis' in ep:
              <p>${ep.synopsis}</p>
            %endif
        </div>
        %endfor
      %endfor
    %else:
      <p>No episode suggestions are available at this moment.</p>

      <p>When you start watching series, this view will show you the most recent episodes that you haven't seen yet, sorted by series .</p>
    %endif
    </div>
    </div>

</div>

</body>
</html>