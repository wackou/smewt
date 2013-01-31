<%inherit file="smewt:templates/common/base_style.mako"/>

<%!
from guessit.textutils import clean_string
from smewt.base.utils import smewtMediaUrl
from smewt.base import EventServer

refresh_icon = smewtMediaUrl('/static/images/view-refresh.png')
delete_icon = smewtMediaUrl('/static/images/edit-delete.png')

def clean_feedtitle(title):
    return title.replace('[ed2k]', '').replace('tvunderground.org.ru:', '')

def clean_eptitle(title):
    return ' - '.join(title.replace('[ed2k] ', '').split(' - ')[1:])

%>

<%
feedWatcher = context.get('feedWatcher')
feeds = feedWatcher.feedList
%>


<script>

function refresh() {
    location.reload(true);
}

function action(action, args, refreshTimeout) {
    $.post("/action/"+action, args)
    .done(function(data) {
        if (data == "OK") {
            if (refreshTimeout) window.setTimeout(refresh, refreshTimeout);
            else                refresh();
        }
        else              { alert("ERROR: "+data); }
    })
    .fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
    .always(function(data) { /* alert("always: "+data); */ });
}

function updateFeed(feedUrl) {
    action('update_feed', { 'feed': feedUrl });
}

function unsubscribeFromFeed(feedUrl) {
    action('unsubscribe', { 'feed': feedUrl });
}

function setLastUpdated(feedUrl, index) {
    action('set_last_update', { 'feed': feedUrl, 'index': index });
}


function checkAllFeeds() {
    action('check_feeds', undefined, refreshTimeout=4000);
}

function clearEventServer() {
    action('clear_event_log');
}


</script>

<div class="container-fluid">
  <div class="row-fluid">

    <table class="table table-striped table-bordered table-hover">
      <thead><tr>
      %for h in ['Title', 'Last episode', 'Actions']:
        <td>${h}</td>
      %endfor
      </tr></thead>
      <tbody>

        %for f in feeds:
        <tr>
          <td>${clean_feedtitle(f['title'])}</td>

          <td id="eps${loop.index}">
              <div class="btn-group">
                <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                  ${clean_eptitle(f['lastTitle'])}
                  <span class="caret"></span>
                </a>
                <ul class="dropdown-menu">
                  %for fd in feedWatcher.feedList[loop.index].get('entries', []):
                  <li><a href="#"
                         onclick="setLastUpdated('${f['url']}', ${loop.index});">
                    ${clean_eptitle(fd['title'])}</a></li>
                  %endfor
                  <li><a href="#">None</a></li>
                </ul>
              </div>

          </td>

          <td>
            <div class="btn" onclick="updateFeed('${f['url']}');"><img src="/static/images/view-refresh.png" width="24" heigth="24"/></div>
            <div class="btn" onclick="unsubscribeFromFeed('${f['url']}');"><img src="/static/images/edit-delete.png" width="24" heigth="24"/></div>
          </td>
        </tr>
        %endfor
      </tbody>
    </table>

    <div class="btn" onclick="checkAllFeeds();">Check all feeds</div>
    <div class="btn" onclick="clearEventServer();">Clear log</div>

<br/><br/>
    <textarea readonly="true" rows="10" class="span12">
      %for event in EventServer.events.events[::-1]:
${event}
      %endfor
    </textarea>
  </div>
</div>
