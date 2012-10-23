<%inherit file="base_style.mako"/>

<%
shows = [ s.replace("'", "") for s in context['shows'] ]
shows_repr = '["' + '","'.join(shows) + '"]'
#print shows_repr

series = context['url'].args.get('series', None)
feeds = context.get('feeds', [])

from smewt.base import utils
import guessit

def flag_url(lang):
    return utils.smewtMediaUrl('common', 'images', 'flags',
                               '%s.png' % guessit.Language(lang).alpha2)

%>


<script>
function getFeeds() {
    var series = $('#tvshow').val();
    mainWidget.feedsForSeries(series);
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
    <hr>
    <%
      subtitles = None
    %>
    <p>
      <b>Audio: <img src="${flag_url(lang)}"/>
      %if subtitles:
       - Subtitles: None
      %endif
      </b>
    </p>

    <table class="table table-striped table-bordered table-hover">
      <thead><tr class="info">
      %for h in ['Format', 'Season', 'Codec', 'Title', 'Status', 'Subtitles', 'Year', 'Link']:
      <td>${h}</td>
      %endfor
      </tr></thead>
      <tbody>

        %for f in fds:
        <tr>
          %for field in f[:5]:
            <td>${field}</td>
          %endfor
          <td>
          %if f[5]:
          <img src="${flag_url(f[5])}"/>
          %endif
          </td>
          <td>${f[6]}</td>
          <td><div class="btn">Subscribe</div></td>
        </tr>
        %endfor
      </tbody>
    </table>
    %endfor
  </div>
  %endif
</div>
