<%inherit file="base.mako"/>

<%block name="style">
<style>

#header {
 margin: 0 0 20px 0;
 background-color: #F0F0F0;
 padding-top: 10px;
 padding-bottom: 10px;
 text-align: center;
 font: bold 18px Verdana, sans-serif;
 color: #333333;
}

.title {
 margin-top: 30px;
 padding-left: 10px;
}

.title a {
 text-decoration: none;
 font: bold 24px Verdana, sans-serif;
 color: #448;
}

.well {
 padding: 10px;
}

/*
.well img {
 position: relative;
 height: 90px;
 float: left;
}
*/

.poster img {
 position: relative;
 height: 90px;
 float: left;
}

</style>
</%block>

<%def name="make_header(title)">
  <div id="header">
    ${title}
  </div>
</%def>

<%def name="make_title_box(img, title, url)">

<div class="well">
  <div class="row-fluid">
    <div class="span2">
    <img src="${img}" class="poster" /></div>
    <div class="span10 title">
  <a href="${url}">${title}</a></div></div>
</div>

</%def>



<%def name="make_navbar(url)">
<%
from guessit.fileutils import split_path
from smewt import SmewtUrl

path = split_path(url.spath.path)
%>

<ul class="breadcrumb">
  <li>
    <a href="${SmewtUrl('media', 'speeddial/')}">media</a> <span class="divider">/</span>
  </li>
  <li>
    <a href="${SmewtUrl('media', path[1] + '/')}">${path[1]}</a> <span class="divider">/</span>
  </li>
  <li class="active">${path[2]}</li>
</ul>
</%def>


## Always have the breadcrumb navigation on top
## requires that the template is always passed the url in its context
<div class="container-fluid" style="margin-top: 10px;">
  ${make_navbar(context['url'])}
</div>


${next.body()}
