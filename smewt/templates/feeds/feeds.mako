<%inherit file="smewt:templates/common/base_style.mako"/>

<%!
from smewt.plugins import tvu
%>

<%
feedWatcher = context.get('feedWatcher')
feeds = feedWatcher.feedList
%>


<%block name="scripts">
  ${parent.scripts()}

<script>

function refreshFunc() {
    location.reload(true);
}

function action(actn, args, refresh, refreshTimeout, refreshCallback) {
    refresh = (typeof refresh !== 'undefined') ? refresh : false;
    refreshCallback = (typeof refreshCallback !== 'undefined') ? refreshCallback : refreshFunc;
    $.post("/action/"+actn, args)
    .done(function(data) {
        if (data == "OK") {
            if (refresh) {
                if (refreshTimeout) window.setTimeout(refreshCallback, refreshTimeout);
                else                refreshCallback();
            }
        }
        else              { alert("ERROR: "+data); }
    })
    .fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
    .always(function(data) { /* alert("always: "+data); */ });
}

function actionRefresh(actn, args, refreshTimeout) {
    return action(actn, args, true, refreshTimeout);
}


function updateFeed(feedUrl) {
    action("update_feed", { "feed": feedUrl }, true, 1000, refreshFeedsStatus);
}

function unsubscribeFromFeed(feedUrl) {
    action("unsubscribe", { "feed": feedUrl }, true);
}

function setLastUpdated(feedUrl, index) {
    action("set_last_update", { "feed": feedUrl, "index": index }, true, 0, refreshFeedsStatus);
}

function mldonkeyStart() {
    action("mldonkey_start");
}

function mldonkeyStop() {
    action("mldonkey_stop");
}

function checkAllFeeds() {
    action("check_feeds");
}

function clearEventServer() {
    action("clear_event_log");
}


function info(name, func) {
    $.get("/info/"+name)
    .done(function(data) {
        func(data);
    })
    //.fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
    .always(function(data) { /* alert("always: "+data); */ });
}


function refreshEventLog() {
    info("event_log", function(data) {
        var newlog = data.substring($("#eventLog").text().length);\
        if (newlog.indexOf('Already') >= 0 ||
            newlog.indexOf('Successfully') >= 0) {
            refreshFeedsStatus();
        }

        var textarea = document.getElementById("eventLog");
        var bottom = (Math.abs((textarea.scrollTop+textarea.offsetHeight) - textarea.scrollHeight) < 20);
        var previous = textarea.scrollTop;
        $("#eventLog").html(data);
        if (bottom) { textarea.scrollTop = textarea.scrollHeight; }
        else        { textarea.scrollTop = previous; }
    });
}


function refreshMLDonkeyStatus() {
    info("mldonkey_online", function(data) {
        var status = '<img src="/static/images/user-busy.png"/> Offline ' +
            '<div class="btn" onclick="mldonkeyStart();">Start MLDonkey</div>';
        if (data) {
            status = '<img src="/static/images/user-online.png"/> Online ' +
            '<div class="btn" onclick="mldonkeyStop();">Stop MLDonkey</div>';
        }
        $("#mldonkeyStatus").html("MLDonkey status:" + status);
    });
}

function refreshFeedsStatus() {
    info("feeds_status", function(data) {
        var rows = $("#feedTable tr");
        if (data.length != rows.length) {
            // not the same number of feeds as rows in our table
            refreshFunc();
        }
        for (var i=0; i<data.length; i++) {
            var feedUrl = data[i][0];
            var feedTitle = data[i][1];
            var last = data[i][2];
            var allEpisodes = data[i][3];

            $("#feedtitle_" + i).html(feedTitle);
            $("#last_" + i).html(last + ' <span class="caret"/>');

            eps = ''
            for (var j=0; j<allEpisodes.length; j++) {
                eps += "<li><a data-target='#' onclick='setLastUpdated(\""+feedUrl+"\","+j+");'>" +
                    allEpisodes[j] + "</a></li>";
            }
            eps += "<li><a data-target='#' onclick='setLastUpdated(\""+feedUrl+"\",-1);'>None</a></li>";
            $("#feed_" + i).html(eps);

        }
    });
}

$(function() {
    refreshEventLog();
    refreshMLDonkeyStatus();
    refreshFeedsStatus();
});

setInterval(refreshEventLog, 2000);
setInterval(refreshMLDonkeyStatus, 2000);

</script>
</%block>


<div class="container-fluid">
  <div class="row-fluid">

    <table class="table table-striped table-bordered table-hover">
      <thead><tr>
      %for h in ['Title', 'Last episode', 'Actions']:
        <td>${h}</td>
      %endfor
      </tr></thead>
      <tbody id="feedTable">

        %for f in feeds:
        <tr>
          <td id="feedtitle_${loop.index}">${tvu.clean_feedtitle(f['title'])}</td>

          <td id="eps${loop.index}">
              <div class="btn-group">
                <a class="btn dropdown-toggle" data-toggle="dropdown"
                   href="#" id="last_${loop.index}">
                  ${tvu.clean_eptitle(f['lastTitle'])}
                  <span class="caret"></span>
                </a>
                <ul class="dropdown-menu" id="feed_${loop.index}">
                </ul>
              </div>

          </td>

          <td>
            <div class="btn" onclick="updateFeed('${f['url']}');">
              <img src="/static/images/view-refresh.png" width="24" heigth="24"/>
            </div>
            <div class="btn" onclick="unsubscribeFromFeed('${f['url']}');">
              <img src="/static/images/edit-delete.png" width="24" heigth="24"/>
            </div>
          </td>
        </tr>
        %endfor
      </tbody>
    </table>

    <div class="span4">
      <div class="btn" onclick="checkAllFeeds();">Check all feeds</div>
      <div class="btn" onclick="clearEventServer();">Clear log</div>
    </div>

    <div class="span6" id="mldonkeyStatus">
    </div>

<br/><br/>
    <textarea readonly="true" rows="10" class="span12" id="eventLog">
    </textarea>
  </div>
</div>
