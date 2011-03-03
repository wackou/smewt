# -*- coding: utf-8 -*-
# Licensed under the MIT license
# http://opensource.org/licenses/mit-license.php
#
# Copyright 2011, Ricard Marxer <ricard@smewt.com>
# Copyright 2011, Caleb Callaway <enlightened-despot@gmail.com>
# Copyright 2007-2010, Frank Scholz <dev@coherence-project.org>
# Copyright 2007, James Livingston  <doclivingston@gmail.com>

import os.path
import coherence.extern.louie as louie
import urllib

from smewt.media.series.serieobject import Series, Episode
from smewt.base.utils import tolist

import mimetypes
mimetypes.init()
mimetypes.add_type('audio/x-m4a', '.m4a')
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/mpegts', '.ts')
mimetypes.add_type('video/divx', '.divx')
mimetypes.add_type('video/divx', '.avi')
mimetypes.add_type('video/x-matroska', '.mkv')


from coherence import __version_info__

from coherence.upnp.core import DIDLLite

from coherence.backend import BackendItem, BackendStore

ROOT_CONTAINER_ID = 0
VIDEO_CONTAINER = 100
SERIES_CONTAINER_ID = 101
MOVIES_CONTAINER_ID = 102

CONTAINER_COUNT = 10000

VIDEO_COUNT = 1000000

# most of this class is from Coherence, originally under the MIT licence

class Container(BackendItem):

    logCategory = 'smewt_media_store'

    def __init__(self, store, name, parent_id, children_callback=None,play_container=False):
        self.id = store.new_item(self)
        self.parent_id = parent_id
        self.name = name
        self.mimetype = 'directory'
        self.store = store
        self.play_container = play_container
        self.update_id = 0
        if children_callback != None:
            self.children = children_callback
        else:
            self.children = []

        
    def add_child(self, child):
        self.children.append(child)

    def get_children(self,start=0,request_count=0):
        if callable(self.children):
            children = self.children(self.id)
        else:
            children = self.children

        self.info("Container get_children %r (%r,%r)", children, start, request_count)
        if request_count == 0:
            return children[start:]
        else:
            return children[start:request_count]

    def get_child_count(self):
        return len(self.get_children())

    def get_item(self, parent_id=None):
        item = DIDLLite.Container(self.id,self.parent_id,self.name)
        item.childCount = self.get_child_count()
        if self.store and self.play_container == True:
            if item.childCount > 0:
                res = DIDLLite.PlayContainerResource(self.store.server.uuid,cid=self.get_id(),fid=str(VIDEO_COUNT + int(self.get_children()[0].get_id())))
                item.res.append(res)
        return item

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id



class SeriesItem(Container):

    logCategory = 'smewt_media_store'

    def __init__(self, store, series, parent_id):
        Container.__init__(self, store, series.title, parent_id, children_callback = self.get_children_implementation)
        self.series = series

    def get_children_implementation(self, parent_id):
        self.warning("SeriesItem.get_children")
        children = []

        for ep in tolist(self.series.episodes):
          children.append(EpisodeItem(self.store, ep, parent_id))
          
        return children


class EpisodeItem(BackendItem):

    logCategory = 'smewt_media_store'

    def __init__(self, store, episode, parent_id):
        self.id = store.new_item(self)
        self.episode = episode
        self.store = store

    def get_children(self,start=0, request_count=0):
        return []
        
    def get_child_count(self):
        return len(self.get_children())

    def get_item(self, parent_id = SERIES_CONTAINER_ID):
        item = DIDLLite.VideoItem(self.id, parent_id, self.episode.title)
        
        # add http resource
        for videoFile in tolist(self.episode.files):
          url = 'file://' + videoFile.filename
          mimetype, _ = mimetypes.guess_type(url, strict=False)
          res = DIDLLite.Resource(url, 'http-get:*:%s:*' % (mimetype,))
          item.res.append(res)

          res = DIDLLite.Resource(url, 'internal:%s:%s:*' % (self.store.server.coherence.hostname, mimetype,))
          item.res.append(res)

        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.episode.title

    def get_cover(self):
        return self.cover

    def get_id(self):
        return self.id

    def get_name(self):
        return self.episode.title



class MediaStore(BackendStore):

    logCategory = 'smewt_media_store'
    implements = ['MediaServer']

    def __init__(self, server, **kwargs):
        BackendStore.__init__(self,server,**kwargs)
        self.warning("__init__ MediaStore %r", kwargs)
        """
        self.wmc_mapping.update({'4': lambda : self.get_by_id(SERIES_CONTAINER_ID),    # all series
                                 '7': lambda : self.get_by_id(MOVIES_CONTAINER_ID)
                                 })
        """
        self.server = server
        self.smewt_db = kwargs.get("smewt_db", None)
        self.urlbase = kwargs.get("urlbase", "")
        self.series = None
        self.episodes = None
        
        self.next_id = 0
        self.items = {}
        self.ids = {}
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "Smewt on %s" % self.server.coherence.hostname

        root_container = Container(self, self.name, -1)

        all_series = Container(self, 'All series', root_container.get_id(), 
                               children_callback = self.children_series,
                               play_container = False)
                          
        root_container.add_child(all_series)

        louie.send('Coherence.UPnP.Backend.init_completed', None, backend=self)

    def get_by_id(self,id):
        self.info("looking for id %r", id)
        if '@' in id:
          id = id.split('@')[0]
        return self.items[int(id)]
        
    def new_item(self, item):
        item_id = self.next_id
        """
        smewt_id = tuple(item.keys())
        if smewt_id in self.ids:
          return self.ids[item]
        """
        self.items[item_id] = item
        #self.ids[smewt_id] = item_id
        
        #print item_id
        
        self.next_id += 1
      
        return item_id

    def upnp_init(self):
        if self.server:
          self.server.connection_manager_server.set_variable(0, 'SourceProtocolInfo',
                             ['internal:%s:video/mp4:*' % self.server.coherence.hostname,
                              'http-get:*:video/mp4:*',
                              'internal:%s:video/x-msvideo:*' % self.server.coherence.hostname,
                              'http-get:*:video/x-msvideo:*',
                              'internal:%s:video/mpeg:*' % self.server.coherence.hostname,
                              'http-get:*:video/mpeg:*',
                              'internal:%s:video/avi:*' % self.server.coherence.hostname,
                              'http-get:*:video/avi:*',
                              'internal:%s:video/divx:*' % self.server.coherence.hostname,
                              'http-get:*:video/divx:*',
                              'internal:%s:video/quicktime:*' % self.server.coherence.hostname,
                              'http-get:*:video/quicktime:*'],
                             default=True)
          self.server.content_directory_server.set_variable(0, 'SystemUpdateID', self.update_id)

        self.warning("__init__ MediaStore initialized")

    def children_series(self, parent_id):
        self.warning("children_series")
        series = []

        if self.smewt_db is None:
          return series
          
        all_series = self.smewt_db.find_all(Series)
        for s in all_series:
          series.append(SeriesItem(self, s, parent_id))
          
        return series