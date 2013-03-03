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

<script type="text/javascript">

function updateFolders(collec, index) {
    var nfolders = $("#collectionTable_" + collec + " tr").length - 1; // for the last line with the add button
    var modifiedFolder = null;
    var folders = [];
    for (var i=0; i<nfolders; i++) {
        var folder_name = $("#folder_" + collec + "_" + i).val()
        if (i == index) modifiedFolder = folder_name;
        folders.push([ folder_name,
                       $("#rec_"    + collec + "_" + i)[0].checked ]);
    }
    action("set_collection_folders", { "collection": collec, "folders": JSON.stringify(folders) },
           true, false, function() { info("exists_path", { path: modifiedFolder }, function(data) {
               if (data) $("#folder_"+collec+"_"+index).css('color', 'green');
               else      $("#folder_"+collec+"_"+index).css('color', 'red');
           }); });
}

function updateBoolProperty(form, w, prop) {
    $.post('/config/set/' + prop,
           { value: form[w].checked });
}

function updateIncomingFolder() {
    $.post('/config/set/incomingFolder',
           { value: $("#incomingFolder").val() },
           function(data) {
               if (data) $("#incomingFolder").css('color', 'green');
               else      $("#incomingFolder").css('color', 'red');
           });
}

</script>
</%block>


<div class="container-fluid">
  <div class="row-fluid">
    <form>

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
                           onKeyUp="updateFolders('${collec.name}', ${loop.index});" onChange="updateFolders('${collec.name}', ${loop.index});"
                           value="${f}" />

                  </td>
                  <td>
                    <% checked = 'checked' if rec else '' %>

                    <input type="checkbox" id="rec_${collec.name}_${loop.index}" name="watched"
                           onClick="updateFolders('${collec.name}', ${loop.index})" ${checked} />
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

            %elif isinstance(value, bool):
            <input type="checkbox" id="w${loop.index}"
              onClick="updateBoolProperty(this.form, 'w${loop.index}', '${prop}');" ${'checked' if value else ''} />

                %if prop == 'tvuMldonkeyPlugin':
                &nbsp;&nbsp;&nbsp;&nbsp;(requires restarting SmewtDaemon)
                %endif


            %elif prop == 'incomingFolder':
            <input id="incomingFolder" type="text" class="span12"
                           onKeyUp="updateIncomingFolder();" onChange="updateIncomingFolder();"
                           value="${value}" />


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
    </form>

  </div>
</div>
