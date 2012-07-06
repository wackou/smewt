<%inherit file="base.mako"/>

<%def name="wells_list(objs)">

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
  %if len(movies) % 2 == 1:
    </div>
  %endif

</%def>

${self.body()}
