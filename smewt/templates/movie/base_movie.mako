<%inherit file="smewt:templates/common/base_style.mako"/>

<%!
import datetime, time
import urllib
from smewt.base.utils import tolist
from smewt import SmewtUrl
%>


<%def name="make_movie_overview(movie)">

<%

def getAll(prop):
    return ', '.join(movie.get(prop) or [])

year = movie.get('year', '')
rating = movie.get('rating', '')
director = getAll('director')
writer = getAll('writer')
genres = getAll('genres')

%>

<div class="well">
  <div class="overview">
    <p><b>year:</b> ${year}</p>
    <p><b>rating:</b> ${rating}</p>
    <p><b>director:</b> ${director}</p>
    <p><b>writer:</b> ${writer}</p>
    <p><b>genres:</b> ${genres}</p>
    %if movie.plot:
      <p><b>plot:</b> ${movie.plot[0]}</p>
      %if len(movie.plot) > 1:
        <p><b>detailed plot:</b> ${movie.plot[1]}</p>
      %endif
    %endif
  </div>
</div>

</%def>


<%def name="make_movie_cast(movie)">

<div class="well">
  %if 'cast' in movie:
    %for person_role in movie.cast:
      <p>${person_role}</p>
    %endfor
  %endif
</div>
</%def>


<%block name="scripts">
${parent.scripts()}

  <script type="text/javascript" charset="utf-8">
    function addComment(form, id, title) {
        action("post_comment", { title: title,
                                 author: 'Me',
                                 contents: form[id].value },
               true);
    }
  </script>
</%block>

<%def name="make_movie_comments(movie, comment_box_width='60%')">
<%
def getComments(md):
    results = []

    for comment in tolist(md.get('comments')):
        results += [ (comment.author,
                      datetime.datetime.fromtimestamp(comment.date).ctime(),
                      comment.text) ]

    return sorted(results, key = lambda x: x[1])

comments = getComments(movie)

# FIXME: need to quote (or do we? TODO: check)
qtitle = urllib.quote(movie.title)

%>

%if comments:
  %for author, atime, comment in comments:
    <p>Comment by <b>${author}</b> at ${atime}<br/>
    <pre>${comment}</pre> </p>
  %endfor
%else:
  <p><em>No Comments yet</em></p>
%endif

<form>
  <textarea rows="4" style="width:${comment_box_width};" columns="80" name="text"></textarea>
  <br>
  <button type="button" onClick="addComment(this.form, 'text', '${qtitle}')">Post new comment</button>
</form>

</%def>


<%def name="make_movie_files(movie)">
<%
allfiles = tolist(movie.get('files'))
for sub in tolist(movie.get('subtitles')):
    allfiles += tolist(sub.get('files'))

# remove duplicates, eg: subfiles appearing more than once as they contain multiple
# languages such as .idx/.sub files
allfiles = set(allfiles)


files = [ (f,
           SmewtUrl('action', 'play', { 'filename1': f.filename }),
           time.ctime(f.lastModified)) for f in allfiles ]

%>

%for f, url, mtime in files:
<div class="well">
  <div class="singlefile">
    <p><a href="${url}">${f.filename}</a></p>
    %for k, v in f.items():
      %if k == 'lastModified':
        <p><b>last scanned on</b>: ${mtime}</p>
      %elif k not in ['metadata', 'filename']:
        <p><b>${k}</b>: ${v}</p>
      %endif
    %endfor
  </div>
</div>
%endfor

</%def>

${next.body()}
