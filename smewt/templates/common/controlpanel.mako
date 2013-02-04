<%inherit file="smewt:templates/common/base_style.mako"/>

<%!
import types
import json
%>

<%
config = context.get('items')
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



function info(name, func) {
    $.get("/info/"+name)
    .done(function(data) {
        func(data);
    })
    //.fail(function(err)   { alert("HTTP error "+err.status+": "+err.statusText); })
    .always(function(data) { /* alert("always: "+data); */ });
}

function updateFolders(collec) {
    var nfolders = $("#collectionTable_" + collec + " tr").length
    var folders = [];
    for (var i=0; i<nfolders; i++) {
        folders.push([ $("#folder_" + collec + "_" + i).val(),
                       $("#rec_"    + collec + "_" + i)[0].checked ]);
    }
    action("set_collection_folders", { "collection": collec, "folders": JSON.stringify(folders) });
}


</script>
</%block>


<div class="container-fluid">
  <div class="row-fluid">

    <div class="btn" onclick="action('rescan');">rescan</div>

  </div>
</div>
