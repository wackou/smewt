<%inherit file="base.mako"/>

<%block name="style">
<style>

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

.well img {
 position: relative;
 height: 90px;
 float: left;
}

</style>
</%block>


<%def name="make_title_box(img, title, url)">

<div class="well">
  <div class="row-fluid">
    <div class="span2">
    <img src="${img}" /></div>
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

${next.body()}
