<%inherit file="smewt:templates/common/base_style.mako"/>

<%
shows = [ s.replace("'", "") for s in context['shows'] ]
shows_repr = '["' + '","'.join(shows) + '"]'
#print shows_repr

series = context['url'].args.get('series', None)
feeds = context.get('feeds', [])
subscribedFeeds = context['subscribedFeeds']

from itertools import groupby
from smewt.base import utils
import guessit

def flag_url(lang):
    return utils.smewtMediaUrl('common', 'images', 'flags',
                               '%s.png' % guessit.Language(lang).alpha2)

def list_langs(lang):
    if not lang:
        return []
    return lang.split('-')

%>


<script>
function getFeeds() {
    var series = $('#tvshow').val();
    mainWidget.feedsForSeries(series);
}

function subscribeToFeed(feedUrl) {
    mainWidget.subscribeToFeed(feedUrl);
}
function unsubscribeFromFeed(feedUrl) {
    mainWidget.unsubscribeFromFeed(feedUrl);
}
</script>

<div class="container-fluid">
  <div class="row-fluid">

    Look for TV show: <input id="tvshow"
    type="text" class="span4" style="margin: 0 auto;"
    data-provide="typeahead"
    data-items="4"
    data-source='${shows_repr}'
    %if series:
      value="${series}"
    %endif
    />

  <button class="btn" onclick="getFeeds();">Get Feeds</button>
  </div>

  %if feeds:
  <div class="row-fluid">
    %for lang, fds in feeds:
    %for sublang, fs in groupby(fds, key=lambda x: x[5]):
    <hr>
    <p>
      <b>Audio:

      %for alang in list_langs(lang):
        <img src="${flag_url(alang)}"/>
      %endfor

      %if sublang:
        &nbsp;&nbsp;&nbsp; Subtitles:

        %for slang in list_langs(sublang):
          <img src="${flag_url(slang)}"/>
        %endfor
      %endif
      </b>
    </p>

    <table class="table table-striped table-bordered table-hover">
      <thead><tr class="info">
      %for h in ['Format', 'Season', 'Codec', 'Title', 'Status', 'Year', 'Link']:
      <td>${h}</td>
      %endfor
      </tr></thead>
      <tbody>


        %for f in fs:
        <tr>
          %for field in f[:5]:
            <td>${field}</td>
          %endfor
          <td>${f[6]}</td>
          %if f[7] in subscribedFeeds:
          <td><div class="btn btn-success" onclick="unsubscribeFromFeed('${f[7]}')">Subscribed!</div></td>
          %else:
          <td><div class="btn" onclick="subscribeToFeed('${f[7]}')">Subscribe</div></td>
          %endif
        </tr>
        %endfor
      </tbody>
    </table>
    %endfor
    %endfor
  </div>
  %endif
</div>
