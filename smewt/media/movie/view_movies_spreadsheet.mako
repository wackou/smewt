
<%!
from smewt import SmewtUrl

class SDict(dict):
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except AttributeError:
            return self[attr]
%>

<%
allmovies = context['movies']

movies = sorted([ SDict({ 'title': m.title,
                    'qtitle': m.title,
                    'year': m.get('year', ''),
                    'rating': m.get('rating') or '-',
                    'genres': ', '.join(m.get('genres') or []) or '-',
                    'watched': 'checked' if m.get('watched') else '',
                    'url': SmewtUrl('media', 'movie/single', { 'title': m.title }),
                    'poster': m.loresImage })
                    for m in allmovies ],
                    key = lambda x: x['title'])

from smewt.base.utils import smewtDirectoryUrl
import_dir = smewtDirectoryUrl('smewt', 'media')

%>

<html>
<head>
  <title>All movies view</title>
   <link rel="stylesheet" href="${import_dir}/movie/movies.css">

        <style type="text/css" title="currentStyle">
            @import "${import_dir}/3rdparty/dataTables/media/css/demos.css";
        </style>

    <script type="text/javascript" language="javascript" src="${import_dir}/3rdparty/dataTables/media/js/jquery.js"></script>
    <script type="text/javascript" language="javascript" src="${import_dir}/3rdparty/dataTables/media/js/jquery.dataTables.js"></script>
    <script type="text/javascript" charset="utf-8">
        function updateAll(form, w, url) {
            mainWidget.updateWatched(url, form[w].checked);
        }

        $(document).ready(function() {
            $('#example').dataTable({});
            $('#example').css('width', '100%');
            $('#example').before('<p>&nbsp;</p>');

        } );
        </script>

</head>



<body>

<div id="wrapper">
    <div id="header">
        ${title} MOVIES
    </div>

    <div id="container"><form>

    <table id="example" class="display">
      <thead>
        <tr><th>Title</th><th>Year</th><th>Rating</th><th>Genres</th><th>Watched</th></tr>
      </thead>
      <tbody>
      %for m in movies:
        <tr>
          <td><a href="${m.url}">${m.title}</a></td>
          <td class="center">${m.year}</td>
          <td class="center">${m.rating}</td>
          <td>${m.genres}</td>
          <td class="center">
            <input type="checkbox" id="w${loop.index}" name="watched"  onClick="updateAll(this.form, 'w${loop.index}', '${m.qtitle}')" ${m.watched} />
          </td>
        </tr>
      %endfor
      </tbody>
      <tfoot>
        <tr><th>Title</th><th>Year</th><th>Rating</th><th>Genres</th><th>Watched</th></tr>
      </tfoot>
    </table>

  </form></div>
</div>

</body>
</html>
