<%inherit file="smewt:templates/common/base_style.mako"/>

<%!
import smewt
import types
import json
%>

<%
config = context.get('items')
%>


<%block name="scripts">
  ${parent.scripts()}

<script>

function refreshTaskManagerStatus() {
    info("task_manager_status", function(data) {
        $("#tmstatus").html(data);
    });
}

$(function() {
    refreshTaskManagerStatus();
});

setInterval(refreshTaskManagerStatus, 1000);


// Select first tab by default
$('#paneltabs a:first').tab('show');

</script>

</%block>

<%def name="make_actions_tab()">
<div class="well">
  Collection
  <div class="btn" onclick="action('rescan_collections');">rescan</div>
  <div class="btn" onclick="action('update_collections');">update</div>
  <div class="btn" onclick="action('clear_collections');">clear</div>
</div>
<div class="well">
  Maintenance
  <div class="btn" onclick="window.open('/user/Smewt.log');">show log</div>
  <div class="btn" onclick="action('clear_cache');">clear cache</div>
  <div class="btn" onclick="action('regenerate_thumbnails');">regenerate speed dial thumbnails</div>
</div>
<hr>
<div class="well">
  Task Manager status: <span id="tmstatus" />
</div>
</%def>

<%def name="make_about_tab()">


<div class="well">
  <b>Smewt: a smart media manager</b>

  <p>&copy;2008-2013 by the Smewt developers</p>
  <a href="http://www.smewt.com">http://www.smewt.com</a><br/>

  <p>Smewt is licensed under the <a href="http://www.gnu.org/licenses/gpl-3.0.txt">GPLv3</a> license.</p>
  <p>Please use <a href="https://github.com/wackou/smewt/issues">https://github.com/wackou/smewt/issues</a> to report bugs.</p>
</div>


<div class="well">

  Smewt is developed by:
  <dl>
    <dt><b>Nicolas Wack</b></dt>
    <dd><a href="mailto:wackou@smewt.com">wackou@smewt.com</a><br/>
    Project Founder, Lead Developer</dd>
    <dt><b>Ricard Marxer</b></dt>
    <dd><a href="mailto:rikrd@smewt.com">rikrd@smewt.com</a><br/>
    Lead Developer</dd>
  </dl>

</div>


<div class="well">
  Special thanks go to:<br/>
  <dl>
    <dt><b><a href="http://www.oxygen-icons.org">The Oxygen Team</a></b></dt>
    <dd>for most of the icons in Smewt and on the website</dd>
    <dt><b><a href="http://www.openclipart.org/user-detail/papapishu">Papapishu</a></b></dt>
    <dd>for the <a href="http://www.openclipart.org/detail/23677">Fried egg</a> icon</dd>
    <dt><b><a href="http://famfamfam.com/">Mark James</a></b></dt>
    <dd>for the <a href="http://famfamfam.com/lab/icons/flags/">flag icons</a></dd>
</div>

</%def>


<div class="container-fluid">
  <div class="row-fluid">
    <div class="span1">
      <img src="/static/images/smewt_64x64.png" />
    </div>
    <div class="span10">
      <br>
      <b>Smewt ${smewt.__version__}</b>
    </div>
  </div>

  <br>

  <div class="row-fluid">
    <div class="tabbable">

      <ul class="nav nav-tabs" id="paneltabs">
        <li><a href="#tab0" data-toggle="tab">SmewtDaemon</a></li>
        <li><a href="#tab1" data-toggle="tab">About</a></li>
      </ul>

      <div class="tab-content">
        <div class="tab-pane" id="tab0">
          ${make_actions_tab()}
        </div>
        <div class="tab-pane" id="tab1">
          ${make_about_tab()}
        </div>
      </div>
    </div>
  </div>

  <div class="row-fluid">
  </div>

</div>
