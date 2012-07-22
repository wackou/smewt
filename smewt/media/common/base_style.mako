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
 //margin-top: 30px;
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

</style>
<%block name="style"/>

<%def name="make_header(title)">
  <div id="header">
    ${title}
  </div>
</%def>

<%def name="make_title_box(img, title, url)">

<div class="well">
  <div class="row-fluid">
    <table><tbody><tr><td>
      <img src="${img}" class="poster" />
    </td><td>
    <div class="title">
      <a href="${url}">${title}</a>
    </div>
    </td></tr></tbody></table>
  </div>
</div>

</%def>



<%def name="make_navbar(url, title=None)">
<%
from guessit.fileutils import split_path
from smewt import SmewtUrl

path = split_path(url.spath.path)
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
        <a href="${SmewtUrl('media', 'speeddial/')}">media</a> <span class="divider">/</span>
      </li>
      <li>
        <a href="${SmewtUrl('media', path[1] + '/')}">${path[1]}</a> <span class="divider">/</span>
      </li>
      <li class="active">${path[-1]}</li>
    </ul>
  </div>
</div>
</%def>


## Always have the breadcrumb navigation on top
## requires that the template is always passed the url in its context
<div class="container-fluid" >
  ${make_navbar(context['url'], context.get('title'))}
</div>



<%def name="make_subtitle_link(subtitle)">
  <%
  sublink = subtitle.subtitleLink()
  %>
  <a href="${sublink.url}"><img src="${sublink.languageImage}" /></a>
</%def>


${next.body()}
