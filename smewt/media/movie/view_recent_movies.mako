<%!
from smewt import SmewtUrl
from smewt.base.utils import tolist
from smewt.base.textutils import toUtf8
import datetime

class SDict(dict):
    def __getattr__(self, attr):
        try:
            return dict.__getattr__(self, attr)
        except AttributeError:
            return self[attr]

def getComments(md):
    results = []

    for comment in tolist(md.get('comments')):
        results += [ (comment.author,
                      datetime.datetime.fromtimestamp(comment.date).ctime(),
                      comment.text) ]

    return sorted(results, key = lambda x: x[1])


def lastViewedString(m):
    lastViewed = datetime.datetime.fromtimestamp(m.lastViewed).date()
    daysago = (datetime.date.today() - lastViewed).days
    datestr = lastViewed.isoformat()

    if daysago == 0:
        return '<b>Today</b> (%s)' % datestr
    elif daysago == 1:
        return '<b>Yesterday</b> (%s)' % datestr
    elif daysago > 1 and daysago < 8:
        return '<b>%d days ago</b> (%s)' % (daysago, datestr)

    return 'on ' + datestr

%>

<%
allmovies = context['movies']

movies = sorted([ SDict({ 'title': m.title,
                    'qtitle': m.title,
                    'year': m.year,
                    'rating': m.get('rating') or '-',
                    'genres': ', '.join(m.get('genres') or []) or '-',
                    'lastViewed': m.lastViewed,
                    'lastViewedString': lastViewedString(m),
                    'watched': 'checked' if m.get('watched') else '',
                    'comments': getComments(m),
                    'url': SmewtUrl('media', 'movie/single', { 'title': m.title }),
                    'poster': m.loresImage }) for m in allmovies ], key = lambda x: -x['lastViewed'])

# keep only the 4 most recent movies
movies = movies[:4]

from smewt.base.utils import smewtDirectoryUrl
import_dir = smewtDirectoryUrl('smewt', 'media')

%>

<html>
<head>
  <title>Recent movies view</title>
  <link rel="stylesheet" href="file://${import_dir}/movie/movies.css">

  <script type="text/javascript" language="javascript" src="file://${import_dir}/3rdparty/dataTables/media/js/jquery.js"></script>

  <script type="text/javascript" charset="utf-8">
    function addComment(form, id, url) {
        mainWidget.addComment(url, 'Me', form[id].value);
    }
  </script>

</head>

<body>

<div id="wrapper">
    <div id="header">
        RECENTLY WATCHED MOVIES
    </div>
    <div id="container"><form>

        <div id="left-side">
      %for m in movies:
      %if loop.index % 2 == 0:
        <div class="commentbox">
          <img src="file://${m.poster}" />
          <a href='${m.url}'>${m.title}</a>
          <div class="comments">
          <p>Last viewed ${m.lastViewedString}</p>
          %if m.comments:
            %for author, time, comment in m.comments:
              <p>Comment by <b>${author}</b> at ${time}:<br/>
              <div class="comment"><pre>${comment}</pre></div> </p>
            %endfor
          %else:
            <p><em>No Comments yet</em></p>
          %endif

          <textarea rows="4" columns="80" name="text${loop.index}"></textarea>
          <button type="button" onClick="addComment(this.form, 'text${loop.index}', '${m.qtitle}')">Post new comment</button>
          </div>
        </div>
      %endif
      %endfor
    </div>

    <div id="right-side">
      %for m in movies:
      %if loop.index % 2 == 1:
        <div class="commentbox">
          <img src="file://${m.poster}" />
          <a href='${m.url}'>${m.title}</a>
          <div class="comments">
          <p>Last viewed ${m.lastViewedString}</p>
          %if m.comments:
            %for author, time, comment in m.comments:
              <p>Comment by <b>${author}</b> at ${time}:<br/>
              <div class="comment"><pre>${comment}</pre></div> </p>
            %endfor
          %else:
            <p><em>No Comments yet</em></p>
          %endif

          <textarea rows="4" columns="80" name="text${loop.index}"></textarea>
          <button type="button" onClick="addComment(this.form, 'text${loop.index}', '${m.qtitle}')">Post new comment</button>
          </div>
        </div>
      %endif
      %endfor
    </div>

  </form></div>
</div>

</body>
</html>
