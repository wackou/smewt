<%!
from smewt import SmewtUrl
from smewt.base.utils import pathToUrl, smewtDirectoryUrl

import_dir = smewtDirectoryUrl('smewt', 'media', 'series')

class SDict(dict):
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except AttributeError:
            return self[attr]
%>

<%
allseries = context['series']
series = sorted([ SDict({ 'title': s.title,
                    'url': SmewtUrl('media', 'series/single', { 'title': s.title }),
                    'poster': pathToUrl(s.get('loresImage')) })
                    for s in allseries ],
                    key = lambda x: x['title'])


%>

<html>
<head>
  <title>All series view</title>
  <link rel="stylesheet" href="file://${import_dir}/series.css">
</head>

<body>

<div id="wrapper">
    <div id="header">
        ALL SERIES
    </div>
    <div id="container">

    %if series:
        <div id="left-side">
      %for s in series[::2]:
        <div class="series">
          <img src="file://${s.poster}" />
          <a href='${s.url}'>${s.title}</a>
        </div>
      %endfor
    </div>

    <div id="right-side">
      %for s in series[1::2]:
        <div class="series">
          <img src="file://${s.poster}" />
          <a href='${s.url}'>${s.title}</a>
        </div>
      %endfor
    </div>
    %else:
      <p>There are no episodes in your library. Make sure you go into <b>Collection -> Select series folders</b> to tell Smewt where to look for them.</p>
    %endif

  </div>
</div>

</body>
</html>
