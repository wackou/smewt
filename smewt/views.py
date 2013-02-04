from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from smewt import SMEWTD_INSTANCE
from smewt.base import Config, EventServer, SmewtException
from smewt.media import Movie, Series, Episode
from smewt.plugins import mldonkey, tvu
from guessit.textutils import reorder_title
import threading
import json


def from_js(value):
    # FIXME: this is a hack
    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        return value


@view_config(route_name='home')
def home_view(request):
    return HTTPFound(location='/speeddial')


@view_config(route_name='all_movies', renderer='smewt:templates/movie/view_all_movies.mako')
def all_movies_view(request):
    return { 'title': 'MOVIES',
             'movies': SMEWTD_INSTANCE.database.find_all(Movie),
             'path': request.current_route_path()
             }

@view_config(route_name='no_movie')
def no_movie(request):
    return HTTPFound(location='/movies')


@view_config(route_name='movie', renderer='smewt:templates/movie/view_movie.mako')
def single_movie_view(request):
    movie = SMEWTD_INSTANCE.database.find_one(Movie, title=request.matchdict['title'])
    return { 'title': movie.title,
             'movie': movie,
             'smewtd': SMEWTD_INSTANCE,
             'path': request.current_route_path()
             }


@view_config(route_name='movies_table',
             renderer='smewt:templates/movie/view_movies_spreadsheet.mako')
def movies_table_view(request):
    return { 'title': 'MOVIE LIST',
             'movies': SMEWTD_INSTANCE.database.find_all(Movie),
             'path': request.current_route_path()
             }

@view_config(route_name='unwatched_movies',
             renderer='smewt:templates/movie/view_movies_spreadsheet.mako')
def unwatched_movies_view(request):
    return { 'movies': [ m for m in SMEWTD_INSTANCE.database.find_all(node_type=Movie)
                         if not m.get('watched') and not m.get('lastViewed') ],
             'title': 'UNWATCHED',
             'path': request.current_route_path()
             }


@view_config(route_name='recent_movies',
             renderer='smewt:templates/movie/view_recent_movies.mako')
def recent_movies_view(request):
    return { 'title': 'RECENT',
             'movies': [ m for m in SMEWTD_INSTANCE.database.find_all(node_type=Movie)
                         if m.get('lastViewed') is not None ],
             'path': request.current_route_path()
             }


@view_config(route_name='all_series',
             renderer='smewt:templates/series/view_all_series.mako')
def series_view(request):
    return { 'title': 'SERIES',
             'series': SMEWTD_INSTANCE.database.find_all(Series),
             'path': request.current_route_path()
             }


@view_config(route_name='media')
def media_view(request):
    from pyramid.httpexceptions import HTTPFound
    return HTTPFound(location='/')


@view_config(route_name='speeddial',
             renderer='smewt:templates/speeddial/speeddial.mako')
def speeddial_view(request):
    return { 'title': 'SPEED DIAL',
             'path': request.current_route_path()
             }

@view_config(route_name='series', renderer='smewt:templates/series/view_episodes_by_season.mako')
def single_series_view(request):
    series = SMEWTD_INSTANCE.database.find_one(Series, title=request.matchdict['title'])
    return { 'title': series.title,
             'series': series,
             'smewtd': SMEWTD_INSTANCE,
             'path': request.current_route_path()
             }

@view_config(route_name='series_suggestions',
             renderer='smewt:templates/series/view_episode_suggestions.mako')
def series_suggestions_view(request):
    return { 'title': 'SUGGESTIONS',
             'episodes': [ ep for ep in SMEWTD_INSTANCE.database.find_all(Episode)
                           if 'lastViewed' in ep ],
             'path': request.current_route_path()
             }


@view_config(route_name='feeds',
             renderer='smewt:templates/feeds/feeds.mako')
def feeds_view(request):
    return { 'title': 'FEEDS',
             'feedWatcher': SMEWTD_INSTANCE.feedWatcher,
             'path': request.current_route_path()
             }


@view_config(route_name='tvu',
             renderer='smewt:templates/tvu/tvu.mako')
def tvu_view(request):
    # do not block if we don't have the full list of shows yet, show what we have
    shows = dict(tvu.get_show_mapping(only_cached=True))

    try:
        series = request.params['series']
        sid = shows[series]
        feeds = tvu.get_seasons_for_showid(sid, title=reorder_title(series))
    except KeyError:
        feeds = []

    subscribedFeeds = [ f['url'] for f in SMEWTD_INSTANCE.feedWatcher.feedList ]

    return { 'title': 'TVU.ORG.RU',
             'shows': shows.keys(), 'feeds': feeds,
             'series': request.params.get('series', None),
             'path': request.current_route_path(),
             'subscribedFeeds': subscribedFeeds
             }


@view_config(route_name='config_get', renderer='json')
def config_get(request):
    config = SMEWTD_INSTANCE.database.config
    return config.get(request.matchdict['name'])


@view_config(route_name='config_set', renderer='json',
             request_method='POST')
def config_set(request):
    config = SMEWTD_INSTANCE.database.config
    try:
        value = from_js(request.POST.get('value') or
                        json.loads(request.body).get('value'))
        config[request.matchdict['name']] = value
        return config[request.matchdict['name']]
    except Exception as e:
        return 'Error: %s' % e


def get_collection(name):
    collection = name.lower()
    if collection == 'movie':
        return SMEWTD_INSTANCE.movieCollection
    elif collection == 'series':
        return SMEWTD_INSTANCE.episodeCollection
    else:
        raise ValueError('Invalid collection name: %s' % name)

@view_config(route_name='action', renderer='json')
def action(request):
    action = request.matchdict['action']

    try:
        if action == 'rescan':
            SMEWTD_INSTANCE.rescanCollections()
            return 'OK'

        elif action == 'clear':
            SMEWTD_INSTANCE.clearDB()
            return 'OK'

        elif action == 'subscribe':
            SMEWTD_INSTANCE.feedWatcher.addFeed(request.params['feed'])
            return 'OK'

        elif action == 'unsubscribe':
            SMEWTD_INSTANCE.feedWatcher.removeFeed(request.params['feed'])
            return 'OK'

        elif action == 'update_feed':
            SMEWTD_INSTANCE.feedWatcher.updateFeedUrl(request.params['feed'])
            return 'OK'

        elif action == 'set_last_update':
            SMEWTD_INSTANCE.feedWatcher.setLastUpdateUrlIndex(request.params['feed'],
                                                              int(request.params['index']))
            return 'OK'

        elif action == 'check_feeds':
            def bg_task():
                SMEWTD_INSTANCE.feedWatcher.checkAllFeeds()
            threading.Thread(target=bg_task).start()
            return 'OK'

        elif action == 'clear_event_log':
            EventServer.events.clear()
            return 'OK'

        elif action == 'mldonkey_start':
            if mldonkey.start():
                return 'OK'
            else:
                return 'Could not find mldonkey executable...'

        elif action == 'mldonkey_stop':
            mldonkey.stop()
            return 'OK'

        elif action == 'set_watched':
            title = unicode(request.params['title'])
            watched = from_js(request.params['watched'])
            SMEWTD_INSTANCE.database.find_one(Movie, title=title).watched = watched
            return 'OK'

        elif action == 'set_collection_folders':
            folders = json.loads(request.params['folders'])
            get_collection(request.params['collection']).setFolders(folders)
            return 'OK'

        elif action == 'add_collection_folder':
            get_collection(request.params['collection']).addFolder()
            return 'OK'

        elif action == 'delete_collection_folder':
            index = int(request.params['index'])
            get_collection(request.params['collection']).deleteFolder(index)
            return 'OK'

        else:
            return 'Error: unknown action: %s' % action

    except SmewtException as e:
        return str(e)

@view_config(route_name='info', renderer='json')
def info(request):
    name = request.matchdict['name']

    if name == 'event_log':
        return '\n'.join(str(ev) for ev in EventServer.events.events)

    elif name == 'mldonkey_online':
        return mldonkey.is_online()

    elif name == 'feeds_status':
        feeds = SMEWTD_INSTANCE.feedWatcher.feedList
        return [ (f['url'],
                  tvu.clean_feedtitle(f['title']),
                  tvu.clean_eptitle(f['lastTitle']),
                  [ tvu.clean_eptitle(fd['title']) for fd in f.get('entries', []) ]
                  ) for f in feeds ]

    else:
        return 'Error: unknown info: %s' % name


@view_config(route_name='preferences',
             renderer='smewt:templates/common/preferences.mako')
def preferences_view(request):
    config = SMEWTD_INSTANCE.database.config
    return { 'title': 'PREFERENCES',
             'smewtd': SMEWTD_INSTANCE,
             'items': config.explicit_items(),
             'path': request.current_route_path()
             }

@view_config(route_name='controlpanel',
             renderer='smewt:templates/common/controlpanel.mako')
def controlpanel_view(request):
    config = SMEWTD_INSTANCE.database.config
    return { 'title': 'CONTROL PANEL',
             'smewtd': SMEWTD_INSTANCE,
             'path': request.current_route_path()
             }
