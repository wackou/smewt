#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib, time, logging, itertools, os.path

from smewt.base.utils import tolist

from coherence.backend import BackendItem, BackendStore
from coherence.upnp.core import DIDLLite
from coherence.upnp.core import utils as coherence_utils

#import smewt
#from smewt.media import Series, Episode, Movie
#from smewt.base import utils, Collection, Media
#from smewt.base.taskmanager import Task, TaskManager

import mimetypes
mimetypes.init()
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mpegts', '.ts')
mimetypes.add_type('video/divx', '.divx')
mimetypes.add_type('video/divx', '.avi')
mimetypes.add_type('video/x-matroska', '.mkv')


LAST_KEY = 'ZZZZZZZ'
CONTAINER_COUNT = 1000

class Container(BackendItem):

    logCategory = 'smewt_media_store'

    def __init__(self, store, name, parent_id):
        self.id = store.new_item(self)
        self.parent_id = parent_id
        self.name = name
        self.mimetype = 'directory'
        self.store = store
        self.update_id = 0
        self.children = []
        
    def add_child(self, child):
        self.children.append(child)

    def add_children(self, children):
        self.children += children

    def get_children(self,start=0,request_count=0):
        children = self.children
        self.info("Container get_children %r (%r,%r)", children, start, request_count)

        if request_count == 0:
            return children[start:]
        else:
            return children[start:request_count]

    def get_child_count(self):
        return len(self.get_children())

    def get_item(self, parent_id=None):
        item = DIDLLite.Container(self.id, self.parent_id, self.name)
        item.childCount = self.get_child_count()
        return item

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

class VideoFileItem(BackendItem):
    logCategory = 'smewt_media_store'

    def __init__(self, store, media, name, parent_id):
        self.id = store.new_item(self)
        self.store = store
        self.media = media
        self.name = name
        self.parent_id = parent_id
        self.item = self.create_item()
        
    def create_item(self):
        item = DIDLLite.VideoItem(self.id, self.parent_id, self.get_name())

        external_url = '%s/%d@%d' % (self.store.urlbase, self.id, self.parent_id,)

        # add http resource
        filename = self.media.filename
        internal_url = 'file://' + filename
        mimetype, _ = mimetypes.guess_type(filename, strict=False)
        size = None
        if os.path.isfile(filename):
          size = os.path.getsize(filename)
        
        res = DIDLLite.Resource(external_url, 'http-get:*:%s:*' % (mimetype,))
        res.size = size
        item.res.append(res)

        res = DIDLLite.Resource(internal_url, 'internal:%s:%s:*' % (self.store.server.coherence.hostname, mimetype,))
        res.size = size
        item.res.append(res)
        
        self.location = filename
        
        return item
        
    def get_children(self,start=0, request_count=0):
        return []
        
    def get_child_count(self):
        return len(self.get_children())
  
    def get_item(self):
        return self.item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_cover(self):
        return self.cover

class VideoItem(BackendItem):
    logCategory = 'smewt_media_store'

    def __init__(self, store, media, name, parent_id):
        self.id = store.new_item(self)
        self.store = store
        self.media = media
        self.name = name
        self.parent_id = parent_id
        self.item = self.create_item()
        
    def create_item(self):
        item = DIDLLite.VideoItem(self.id, self.parent_id, self.get_name())

        external_url = '%s/%d@%d' % (self.store.urlbase, self.id, self.parent_id,)

        # add http resource
        for videoFile in tolist(self.media.files):
          filename = videoFile.filename
          internal_url = 'file://' + filename
          mimetype, _ = mimetypes.guess_type(filename, strict=False)
          size = None
          if os.path.isfile(filename):
            size = os.path.getsize(filename)
          
          res = DIDLLite.Resource(external_url, 'http-get:*:%s:*' % (mimetype,))
          res.size = size
          item.res.append(res)

          res = DIDLLite.Resource(internal_url, 'internal:%s:%s:*' % (self.store.server.coherence.hostname, mimetype,))
          res.size = size
          item.res.append(res)
          
          # FIXME: Handle correctly multifile videos
          self.location = filename
          
        for subtitle in tolist(self.media.get('subtitles')):
          for subfile in tolist(subtitle.files):
            subfilename = subfile.filename
            if os.path.isfile(subfilename):
              # check for a subtitles file
              hash_from_path = str(id(subfilename))
              mimetype = 'smi/caption'
              new_res = DIDLLite.Resource(external_url+'?attachment='+hash_from_path,
                                          'http-get:*:%s:%s' % (mimetype, '*'))
              new_res.size = os.path.getsize(subfilename)
              item.res.append(new_res)
              if not hasattr(item, 'attachments'):
                  item.attachments = {}
              
              item.attachments[hash_from_path] = coherence_utils.StaticFile(subfilename)

        return item
        
    def get_children(self,start=0, request_count=0):
        return []
        
    def get_child_count(self):
        return len(self.get_children())
  
    def get_item(self):
        return self.item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_cover(self):
        return self.cover

def recursiveContainer(store, items, view_funcs, prefix='', parent_id=-1):
    nameMethod = lambda x: x
    sortItems = lambda x: x
    if len(view_funcs) > 0:
      nameMethod = view_funcs[0].get('name', lambda x: x)
      sortItems = view_funcs[0].get('sortItems', lambda x: x)
      itemClass = view_funcs[0].get('item', None)
      
    items = sortItems(items)
    if len(view_funcs) == 0 or 'groupItems' not in view_funcs[0]:
      children = []
      unknown = None
      for i in items:
        if itemClass is None:
          files = tolist(i.files)
          if len(files)>0 and 'title' in i and i.title == 'Unknown':
            # These unguessed files are matched to a movie named 'Unknown'
            unknown = Container(store, 'Unknown', parent_id)
            #print '%s%s [%d]' % (prefix, unicode('Unknown'), unknown.id, )
            for f in tolist(i.files):
              newitem = VideoFileItem(store, f, unicode(os.path.basename(f.filename)), parent_id)
              #print '  %s%s [%d]' % (prefix, unicode(os.path.basename(f.filename)), newitem.id, )
              unknown.add_child(newitem)
          else:
            # These are the normal files
            newitem = VideoItem(store, i, unicode(nameMethod(i)), parent_id)
            #print '%s%s [%d]' % (prefix, unicode(nameMethod(i)), newitem.id, )
            children.append(newitem)
        else:
          newitem = itemClass(store, i, unicode(nameMethod(i)), parent_id)
          #print '%s%s [%d]' % (prefix, unicode(nameMethod(i)), newitem.id, )
          children.append(newitem)
          
      if unknown is not None:
        children.append(unknown)
      return children
    
    groupItems = view_funcs[0]['groupItems']
    
    group = groupItems(items)
    
    children = []
    for k, v in group:
      cont = Container(store, unicode(nameMethod(k)), parent_id)
      #print '%s%s [%d]' % (prefix, unicode(nameMethod(k)), cont.id, )
      cont.add_children( recursiveContainer(store, list(v), view_funcs[1:], parent_id = cont.id, prefix = ' ' + prefix) )
      children.append(cont)
      
    return children
    
def groupByProperty(items, prop, getProperty = None, default = 'Other'):
  groups = {}
  
  if getProperty is None:
    getProperty = lambda x: x.get(prop, None)
  
  for item in items:
    for g in (getProperty(item) or [default]):
      groups.setdefault(g, []).append(item)

  for k, v in groups.items():
    groups[k] = list(set(groups[k]))
  
  return sorted(groups.items(), key=lambda x: x[0] if x[0] is not default else LAST_KEY)

def is_available(x):
  return any([os.path.isfile(f.filename) for f in tolist(x.files)])

def moviesByProperty(store, database, prop, parent_id=-1, only_available=True, getProperty = None, default='Other'):
  moviesItems = lambda db: tolist(db.find_all('Movie'))
  if only_available:
    moviesItems = lambda db: list(itertools.ifilter(is_available, tolist(db.find_all('Movie'))))
  
  moviesViews = [
  {
    'groupItems': lambda sortedItems: groupByProperty(sortedItems, prop, getProperty=getProperty, default=default),
    'name': lambda k: k
  },
  {
    'sortItems': lambda items: sorted(items, key = lambda i: i.title),
    'name': lambda k: k.title if 'title' in k else 'UNKNOWN'
  }
  ]

  items = moviesItems(database)
  return recursiveContainer(store, items, moviesViews, parent_id=parent_id)

def allSeries(store, database, parent_id=-1, only_available=True):
  seriesItems = lambda db: tolist(db.find_all('Episode'))
  if only_available:
    seriesItems = lambda db: list(itertools.ifilter(is_available, tolist(db.find_all('Episode'))))

  seriesViews = [
  {
    'sortItems': lambda items: sorted(items, key = lambda i: i.series.title),
    'groupItems': lambda sortedItems: itertools.groupby(sortedItems, key=lambda i: i.series),
    'name': lambda k: k.title if 'title' in k else 'UNKNOWN'
  },
  {
    'sortItems': lambda items: sorted(items, key = lambda i: i.season),
    'groupItems': lambda sortedItems: itertools.groupby(sortedItems, key=lambda i: i.season),
    'name': lambda k: 'Season %d' % (k,)
  },
  {
    'sortItems': lambda items: sorted(items, key = lambda i: int(i.episodeNumber)),
    'name': lambda k: '%3d - %s' % (k.get('episodeNumber', 0), k.get('title', tolist(k.get('files', []))[0].get('filename', '[unknown]')), ) 
  }
  ]

  items = seriesItems(database)
  return recursiveContainer(store, items, seriesViews, parent_id=parent_id)
  
def allMovies(store, database, parent_id=-1, only_available=True):
  moviesItems = lambda db: tolist(db.find_all('Movie'))
  if only_available:
    moviesItems = lambda db: list(itertools.ifilter(is_available, tolist(db.find_all('Movie'))))

  moviesViews = [
  {
    'sortItems': lambda items: sorted(items, key = lambda i: i.title),
    'name': lambda k: k.title if 'title' in k else '[unknown]'
  }
  ]
  
  items = moviesItems(database)
  return recursiveContainer(store, items, moviesViews, parent_id=parent_id)

def advSeries(store, database, parent_id=-1, only_available=True):  
  def isEpisode(m):
    from smewt.media.series.serieobject import Episode
    return os.path.isfile(m.filename) and any([any([mdlink.isinstance(Episode) for mdlink in mds]) for mds in tolist(m.metadata)])
    
  seriesItems = lambda db: list(db.find_all(node_type = 'Media', valid_node = isEpisode))

  seriesViews = [
  {
    'sortItems': lambda items: sorted(items, key = lambda i: tolist(i.metadata)[0].series.title),
    'groupItems': lambda sortedItems: itertools.groupby(sortedItems, key=lambda i: tolist(i.metadata)[0].series),
    'name': lambda k: k.title if 'title' in k else 'UNKNOWN'
  },
  {
    'sortItems': lambda items: sorted(items, key = lambda i: tolist(i.metadata)[0].season),
    'groupItems': lambda sortedItems: itertools.groupby(sortedItems, key=lambda i: tolist(i.metadata)[0].season),
    'name': lambda k: 'Season %d' % (k,)
  },
  {
    'sortItems': lambda items: sorted(items, key = lambda i: (int(tolist(i.metadata)[0].episodeNumber), i.filename)),
    'name': lambda k: '%3d - %s' % (tolist(k.metadata)[0].get('episodeNumber', 0), tolist(k.metadata)[0].get('title', os.path.basename(k.get('filename', '[unknown]'))), ), 
    'item': VideoFileItem
  }
  ]

  items = seriesItems(database)
  return recursiveContainer(store, items, seriesViews, parent_id=parent_id)
 
if __name__ == '__main__':
  from pygoo import *
  logging.basicConfig(level=logging.WARNING)
  log = logging.getLogger('upnp_smewt')

  dbfile = unicode('/home/rmarxer/.config/Falafelton/Smewt-dev.database')

  class FakeCoherence:
    hostname = 'fake'

  class FakeServer:
    coherence = FakeCoherence()

  class FakeStore(BackendStore):
    def __init__(self, urlbase=''):
      self.urlbase = urlbase
      self.items = {}
      self.server = FakeServer()
      self.last_int = 0
      
    def new_item(self, item):
      id = self.last_int
      self.items[id] = item
      self.last_int += 1
      return id

  class VersionedMediaGraph(MemoryObjectGraph):
      def add_object(self, node, recurse = Equal.OnIdentity, excluded_deps = list()):
          result = super(VersionedMediaGraph, self).add_object(node, recurse, excluded_deps)
          if isinstance(result, Media):
              result.lastModified = time.time()

          return result
          
  database = VersionedMediaGraph()
  try:
    database.load(dbfile)
  except:
      log.warning('Could not load database %s', dbfile)

  store = FakeStore()
  
  advSeries(store, database)
  allSeries(store, database)
  allMovies(store, database)
  moviesByProperty(store, database, 'genres')
  moviesByProperty(store, database, 'director')
  moviesByProperty(store, database, 'cast', getProperty = lambda x: [act.split('--')[0] for act in x.get('cast', [])])
  moviesByProperty(store, database, 'year', getProperty = lambda x: [x.get('year', None)])
  