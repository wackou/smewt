<%inherit file="base.mako"/>
<%!
from guessit.language import ALL_LANGUAGES, Language
from guessit.fileutils import split_path
import urllib
%>


<style>
body {
    padding-top: 10px;
}

#header {
    margin: 0 0 20px 0;
    background-color: #F0F0F0;
    padding-top: 6px;
    padding-bottom: 6px;
    text-align: center;
    font: bold 18px Verdana, sans-serif;
    color: #333333;
}

.title {
    padding-left: 20px;
}

.title a {
    text-decoration: none;
    font: bold 24px Verdana, sans-serif;
    color: #448;
}

.well {
    padding: 10px;
    margin-bottom: 10px;
}

.poster img {
    position: relative;
    height: 90px;
    float: left;
}

.sidenav {
    position: fixed;
}

</style>
<%block name="style"/>

<%def name="make_header(title)">
  <div id="header">
    ${title}
  </div>
</%def>

<%def name="make_poster_title(img, title, url)">
    <table><tbody><tr><td>
      <div class="poster"><img src="${img}" /></div>
    </td><td>
    <div class="title">
      <a href="${url}">${title}</a>
    </div>
    </td></tr></tbody></table>
</%def>

<%def name="make_title_box(img, title, url)">
<div class="well">
  <div class="row-fluid">
    ${make_poster_title(img, title, url)}
  </div>
</div>
</%def>

<%def name="make_lang_selector(smewtd)">
<%!
langs = sorted(l.english_name.replace("'", "") for l in ALL_LANGUAGES)
langs_repr = '["' + '","'.join(langs) + '"]'
%>

<%
from smewt import SMEWTD_INSTANCE
config = SMEWTD_INSTANCE.database.config

sublang = ''
if config.get('subtitleLanguage'):
    sublang = Language(config.subtitleLanguage).english_name

%>

<input id="sublang" type="text" class="span2" style="margin: 0 auto;" data-provide="typeahead" data-items="4" data-source='${langs_repr}' onKeyUp="return sublangChanged()" onChange="return sublangChanged()" value="${sublang}" />
</%def>

<%def name="make_media_box(f)">
<div class="well">
  <a href="javascript:void(0);" onclick="play_file('${urllib.quote(f.filename)}');">${f.filename}</a>
</div>
</%def>

<%def name="make_navbar(path, title=None)">
<%
path = path.split('/')

crumbs = []

for i, p in enumerate(path[1:]):
    crumbs += [ (urllib.unquote(p), '/' + '/'.join(path[1:2+i])) ]
%>

<div class="row-fluid">
  <div class="span4">
    %if title:
    ${make_header(title)}
    %else:
    ${make_header(path[-1])}
    %endif
  </div>

  <div class="span8">
    <ul class="breadcrumb">
      <li>
        <a href="/"><i class="icon-home"></i></a> <span class="divider">/</span>
      </li>

      %for text, crumbUrl in crumbs[:-1]:
      <li>
        <a href="${crumbUrl}">${text}</a> <span class="divider">/</span>
      </li>
      %endfor

      <li class="active">${crumbs[-1][0]}
      %if getattr(url, 'args', None):
      &nbsp;<em>(${', '.join('%s = %s' % (k, v) for k, v in url.args.items())})</em>
      %endif
      </li>
    </ul>
  </div>
</div>
</%def>


<%def name="navlink(title, target, newtab=False)">
  <%
  targetlink = '/' + target
  active = (context['path'] == target)
  %>
  <li
      %if active:
      class="active"
      %endif:
      ><a href="${target}"
      %if newtab:
      target="_blank"
      %endif:
      >${title}</a></li>
</%def>

<%def name="video_control()">

Video Control:
<div class="btn" onclick="action('video_fback');"> <i class="icon-fast-backward"></i> </div>
<div class="btn" onclick="action('video_back');"> <i class="icon-backward"></i> </div>

<div class="btn" onclick="action('video_pause');"> <i class="icon-pause"></i> </div>
<div class="btn" onclick="action('video_stop');"> <i class="icon-stop"></i> </div>

<div class="btn" onclick="action('video_fwd');"> <i class="icon-forward"></i> </div>
<div class="btn" onclick="action('video_ffwd');"> <i class="icon-fast-forward"></i> </div>

&nbsp;&nbsp;&nbsp; Pos: <span id="videoPos"></span>

</%def>

<%
from smewt import SMEWTD_INSTANCE
config = SMEWTD_INSTANCE.database.config
%>

<div class="container-fluid" >
  <div class="row-fluid">
    <div class="span2 sidebar">

      ## Main navigation list
      <ul class="nav nav-list span2 sidenav">
        <li class="nav-header">General</li>
        ${navlink('Speed dial', '/speeddial')}
        %if config.get('tvuMldonkeyPlugin'):
        ${navlink('Tv Underground', '/tvu')}
        ${navlink('Feeds', '/feeds')}
        ${navlink('MLDonkey', 'http://127.0.0.1:4080', True)}
        %endif
        ${navlink('Preferences', '/preferences')}
        ${navlink('Control Panel', '/controlpanel')}
        <li class="nav-header">Movies</li>
        ${navlink('All', '/movies')}
        ${navlink('Table', '/movies/table')}
        ${navlink('Recent', '/movies/recent')}
        ${navlink('Unwatched', '/movies/unwatched')}
        <li class="nav-header">Series</li>
        ${navlink('All', '/series')}
        ${navlink('Suggestions', '/series/suggestions')}
      </ul>

    </div>
    <div class="span10">

      ## Always have the breadcrumb navigation on top
      ## requires that the template is always passed the url in its context
      <div class="container-fluid" >
        ${make_navbar(context['path'], context.get('title'))}
      </div>

      ${next.body()}

    </div>
  </div>
</div>

<%block name="scripts">
  ${parent.scripts()}

  <script type="text/javascript">
    $('.sidenav').affix();

    function sublangChanged(t) {
        var s = $("#sublang");
        $.post("/config/set/subtitleLanguage", { "value": s.val() });
    }

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
            else { alert(data); }
        })
        .fail(function(err) {
            if (err.status == 0) alert("SmewtDaemon doesn't seem to be running...");
            else alert("HTTP error "+err.status+": "+err.statusText);
        })
        //.always(function(data) { alert("always: "+data); })
        ;
    }

    function info(name, args, func) {
        $.get("/info/"+name, args)
        .done(function(data) {
            func(data);
        })
        //.fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
        //.always(function(data) { alert("always: "+data); })
        ;
    }

    function refreshVideoPos() {
        info("video_position", undefined, function(data) {
            $("#videoPos").html(data);
        });
    }

    $(function() {
        refreshVideoPos();
        setInterval(refreshVideoPos, 1000);
    });


  </script>
</%block>
