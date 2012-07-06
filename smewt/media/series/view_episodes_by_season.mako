<%!
from itertools import groupby
from collections import defaultdict
from smewt import SmewtUrl, Media
from smewt.media import Episode, Series, Subtitle
from smewt.base.utils import pathToUrl, smewtDirectoryUrl, tolist
from smewt.base import SmewtException
from smewt.base.actionfactory import PlayAction
import guessit

import os, os.path
import_dir = smewtDirectoryUrl('smewt', 'media')
flags_dir = smewtDirectoryUrl('smewt', 'media', 'common', 'images', 'flags')

class SDict(dict):
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except AttributeError:
            return self[attr]

%>

<%
series = context['series']
displaySynopsis = context['displaySynopsis']

seasons = defaultdict(lambda: [])

seriesName = series.title
poster = pathToUrl(series.get('hiresImage'))
if displaySynopsis:
    displayStyle = 'inline'
else:
    displayStyle = 'none'

# First prepare the episodes
episodes = SDict()

for ep in tolist(series.episodes):
    md = SDict(ep.literal_items())


    # FIXME: we should do sth smarter here, such as ask the user, or at least warn him
    files = ep.get('files')
    if not files:
        # dirty fix so we don't crash if the episode has no associated video file:
        md['filename'] = ''
    elif isinstance(files, list):
        md['filename'] = files[0].filename
    else:
        md['filename'] = files.filename

    md['url'] = SmewtUrl('action', 'play', { 'filename1': md['filename'] })
    md['subtitleUrls'] = []

    languageFiles = defaultdict(lambda: [])
    subtitles = []

    if files:
        for subtitle in tolist(ep.get('subtitles')):
            for subfile in tolist(subtitle.files):
                subtitleFilename = subfile.filename
                # we shouldn't need to check that they start with the same prefix anymore, as the taggers/guessers should have mapped them correctly
                mediaFilename = [ f.filename for f in tolist(files) ] # if subtitleFilename.startswith(os.path.splitext(f.filename)[0]) ]
                mediaFilename = mediaFilename[0] # FIXME: check len == 1 all the time

                # FIXME: subtitle.language should be a guessit.Language, data model needs to be fixed
                languageFiles[guessit.Language(subtitle.language)] += [ (mediaFilename, subtitleFilename) ]

    # prepare links for playing movie with subtitles
    for lang, sfiles in languageFiles.items():
        subtitles.append(SDict({'languageImage': flags_dir + '/%s.png' % lang.alpha2,
                                'url': PlayAction(sfiles).url()}))

    subtitles.sort(key = lambda x: x['languageImage'])

    md['subtitleUrls'] = subtitles

    if 'title' not in md:
        md['title'] = md['filename']

    episodes[(ep.season, ep.episodeNumber)] = md

for md in episodes.values():
    seasons[ md['season'] ].append( md )

for season, eps in seasons.items():
    seasons[season] = sorted(eps, key = lambda x: x['episodeNumber'])

lastSeasonWatched = series.get('lastSeasonWatched', 0)

%>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <title>single serie display</title>

    <script type="text/javascript">
        var tabberOptions = { 'onClick': function(args) {
                                            var t = args.tabber;
                                            var i = args.index;
                                            mainWidget.lastSeasonWatched("${seriesName}", t.tabs[i].headingText.split(' ')[1]);
                                            } };
    </script>

    <script type="text/javascript" src="${import_dir}/3rdparty/tabber.js"></script>
    <script type="text/javascript" src="${import_dir}/3rdparty/styler.js"></script>
    <link rel="stylesheet" href="${import_dir}/series/series.css" type="text/css">

    <script type="text/javascript" charset="utf-8">
        function toggleSynopsis() {
            toggleByName('synopsis');
            mainWidget.toggleSynopsis(isToggled('synopsis'));
        }
    </script>

</head>

<body>

<img src="${poster}" height="130px" width:"auto"/>

<div class="rightshifted">
  <h1>${seriesName}</h1>

  <a href="javascript:toggleSynopsis()">Toggle synopsis</a>
</div>


<div class="tabber">
%for seasonNumber, eps in seasons.items():
  %if seasonNumber == lastSeasonWatched:
    <div class="tabbertab tabbertabdefault">
  %else:
    <div class="tabbertab">
  %endif
  <h2>Season ${seasonNumber}</h2>
  <p>

  %if seriesName != 'Unknown':

  <%
englishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': seriesName, 'season': seasonNumber, 'language': 'en' })
frenchSubsLink  = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': seriesName, 'season': seasonNumber, 'language': 'fr' })
spanishSubsLink = SmewtUrl('action', 'getsubtitles', { 'type': 'episode', 'title': seriesName, 'season': seasonNumber, 'language': 'es' })
  %>
    <div class="boxlink">
      <a href="${englishSubsLink}">Get missing English subtitles</a>
      <a href="${frenchSubsLink}">Get missing French subtitles</a>
      <a href="${spanishSubsLink}">Get missing Spanish subtitles</a>
    </div>

  %for ep in [ ep for ep in eps if 'title' in ep and ep.get('episodeNumber', -1) != -1 ]:
    %if 'filename' in ep:
      %try:
        <div class="episode"><a href="${ep.url}">${ep.episodeNumber} - ${ep.title} </a>
      %except:
        <div class="episode"> ? - ${ep.title}
      %endtry

      %for s in ep['subtitleUrls']:
           <a href="${s.url}"><img src="${s.languageImage}" /></a>
      %endfor

      %if 'synopsis' in ep:
        <div name="synopsis" style="display:${displayStyle}"><p>${ep.synopsis}</p></div>
      %endif
      </div>
    %endif
  %endfor

<%
import os.path
eps = [ ep for ep in tolist(series.get('episodes')) if ep.episodeNumber == -1 and ep.get('files') ]

files = []
for ep in eps:
    files += [ f.filename for f in tolist(ep.files) ]

extras = [ { 'title': f,
             'url': SmewtUrl('action', 'play', { 'filename1': f })
             }
             for f in files ]
%>

  %if extras:
    <div class="extras">Extras / Untitled / Metadata unknown</div>
  %endif
  %for ep in extras:
    <div class="episode"><a href="${ep.url}"><i>${ep.title}</i></a></div>
  %endfor


    %else:
    <!-- series == unknown -->

<%
files = []
for ep in tolist(series.get('episodes')):
    files += [ f.filename for f in tolist(ep.files) ]

unknownFiles = [ { 'title': f,
                   'url': SmewtUrl('action', 'play', { 'filename1': f })
                   }
                   for f in files ]

unknownFiles.sort(key = lambda f: f['title'])

%>

    %for ep in unknownFiles:
        <div class="episode"><a href="${ep.url}"><i>${ep.title}</i></a></div>
    %endfor

    %endif
  </p></div>
%endfor

</body>
</html>
