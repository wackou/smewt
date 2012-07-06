<%inherit file="base.mako"/>

<%block name="list_style">
<style>
#header {
 margin: 10px 0 20px 0;
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

.well img {
 position: relative;
 height: 90px;
 float: left;
}

</style>
</%block>

<div class="container-fluid">


<%block name="navbar">
<%
from guessit.fileutils import split_path
from smewt import SmewtUrl

url = context['url']
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
</%block>

  <div id="header">
    <%block name="list_header"/>
  </div>

  ${next.body()}

</div>


<%def name="wells_list(objs)">

  %for i, obj in enumerate(objs):
    %if i % 2 == 0:
      <div class="row-fluid">
    %endif

    <div class="span6">
      <div class="well">
        <div class="row-fluid">
          <div class="span2">
          <img src="${obj.poster}" /></div>
          <div class="span10 title">
            <a href="${obj.url}">${obj.title}</a></div></div>
      </div>
    </div>

    %if i % 2 == 1:
      </div>
    %endif
  %endfor

  ## close the last line if not done already
  %if len(objs) % 2 == 1:
    </div>
  %endif

</%def>
