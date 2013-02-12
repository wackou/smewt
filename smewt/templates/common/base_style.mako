<%inherit file="base.mako"/>

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
from guessit.language import ALL_LANGUAGES, Language

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
<%
from smewt.base import SmewtUrl
%>
<div class="well">
  <a href="${SmewtUrl('action', 'play', {'filename1': f.filename })}">${f.filename}</a>
</div>
</%def>

<%def name="make_navbar(path, title=None)">
<%
from guessit.fileutils import split_path
from smewt import SmewtUrl
import urllib2

path = path.split('/')

crumbs = []

for i, p in enumerate(path[1:]):
    crumbs += [ (urllib2.unquote(p), '/' + '/'.join(path[1:2+i])) ]

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

<%def name="make_subtitle_flag(subtitle)">
  <%
  sublink = subtitle.subtitleLink()
  %>
  <img src="${sublink.languageImage}" />
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

<div class="container-fluid" >
  <div class="row-fluid">
    <div class="span2 sidebar">

      ## Main navigation list
      <ul class="nav nav-list span2 sidenav">
        <li class="nav-header">General</li>
        ${navlink('Speed dial', '/speeddial')}
        ${navlink('Tv Underground', '/tvu')}
        ${navlink('Feeds', '/feeds')}
        ${navlink('MLDonkey', 'http://127.0.0.1:4080', True)}
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

  <script>
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
            else              { alert(data); }
        })
        .fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
        .always(function(data) { /* alert("always: "+data); */ });
    }

    function info(name, func) {
        $.get("/info/"+name)
        .done(function(data) {
            func(data);
        })
        //.fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
        //.always(function(data) { alert("always: "+data); })
        ;
    }

  </script>
</%block>
