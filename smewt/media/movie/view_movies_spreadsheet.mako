<%inherit file="base_style.mako"/>


<%!
from smewt import SmewtUrl
from smewt.base.utils import SDict, pathToUrl, smewtDirectoryUrl, smewtMediaUrl

dataTables = smewtDirectoryUrl('smewt', 'media', '3rdparty', 'DataTables-1.9.2', 'media')

def media(filename):
    return smewtMediaUrl('common', filename)

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

%>

<%block name="style">
  ${parent.style()}
  <link rel="stylesheet" type="text/css" href="${dataTables}/css/DT_bootstrap.css">
</%block>

<%block name="scripts">
    <script src="${dataTables}/js/jquery.dataTables.js"></script>
    <script src="${dataTables}/js/DT_bootstrap.js"></script>
    <script>
        function updateAll(form, w, url) {
            mainWidget.updateWatched(url, form[w].checked);
        }
    </script>
</%block>



<div class="container-fluid">

  ${parent.make_header('MOVIES')}

  <form>

    <table cellpadding="0" cellspacing="0" border="0" class="table table-striped table-bordered" id="example">
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

  </form>
</div>
