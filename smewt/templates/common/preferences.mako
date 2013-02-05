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
    var nfolders = $("#collectionTable_" + collec + " tr").length - 1; // for the last line with the add button
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

    <table class="table table-striped table-bordered table-hover">
      <thead><tr>
      %for h in ['Property', 'Value']:
        <td>${h}</td>
      %endfor
      </tr></thead>
      <tbody id="configTable">

        %for prop, value in config:
        <tr>
          <td id="prop_${loop.index}">${prop}</td>
          <td id="value_${loop.index}">

            %if prop == 'subtitleLanguage':
              ${parent.make_lang_selector(context['smewtd'])}

            %elif prop == 'collections':
            %for collec in value:
            ${collec.name} collection:
            <table class="table table-striped table-bordered table-hover">
              <thead><tr>
                %for h in ['Folder', 'Recursive', 'Remove']:
                <td>${h}</td>
                %endfor
              </tr></thead>
              <tbody id="collectionTable_${collec.name}">
                %for f, rec in json.loads(collec.folders):
                <tr>
                  <td>
                    <input id="folder_${collec.name}_${loop.index}" type="text" class="span12"
                           onKeyUp="return updateFolders('${collec.name}')" onChange="return updateFolders(${collec.name})"
                           value="${f}" />

                  </td>
                  <td>
                    <% checked = 'checked' if rec else '' %>

                    <input type="checkbox" id="rec_${collec.name}_${loop.index}" name="watched"
                           onClick="updateFolders('${collec.name}')" ${checked} />
                 </td>
                 <td>
                   <div class="btn" onclick="action('delete_collection_folder',
                                                    { 'collection': '${collec.name}',
                                                      'index': ${loop.index} }, true);">
                     <img src="/static/images/edit-delete.png" width="24" heigth="24"/>
                   </div>
                 </td>
                </tr>
                %endfor
                <tr>
                  <td colspan="3">
                   <div class="btn" onclick="action('add_collection_folder', {'collection': '${collec.name}' }, true);">
                     <img src="/static/images/folder-new.png" width="24" heigth="24"/>
                     Add new folder
                   </div>
                  </td>
                </tr>
              </tbody>
            </table>
            %endfor

            %elif prop == 'feeds':
            <table class="table table-striped table-bordered table-hover">
              <thead><tr>
                %for h in ['Title', 'Last episode']:
                <td>${h}</td>
                %endfor
              </tr></thead>
              <tbody id="feedTable">
                %for f in value:
                <tr><td>${f.title}</td><td>${f.lastTitle}</td></tr>
                %endfor
              </tbody>
            </table>


            %elif type(value) is types.GeneratorType:
              ${list(value)}

            %else:
              ${value}

            %endif
          </td>
        </tr>
        %endfor
      </tbody>
    </table>

  </div>
</div>
