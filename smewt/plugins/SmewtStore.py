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

    def __init__(self, id, parent_id, name, children_callback=None,store=None,play_container=False):
        self.id = id
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



class Series(BackendItem):

    logCategory = 'smewt_media_store'

    def __init__(self, store, series, id, parent_id):
        self.id = id
        self.series = series
        self.store = store

    def get_children(self,start=0,request_count=0):
        children = []

        for ep in self.series.episodes:
          children.append(Episode(store, ep, ep.node.id, self.id))

        if request_count == 0:
            return children[start:]
        else:
            return children[start:request_count]

    def get_child_count(self):
        return len(self.get_children())

    def get_item(self, parent_id = SERIES_CONTAINER_ID):
        item = DIDLLite.VideoBroadcast(self.id, parent_id, self.series.title)

        if __version_info__ >= (0,6,4):
            if self.get_child_count() > 0:
                res = DIDLLite.PlayContainerResource(self.store.server.uuid, cid=self.get_id(), fid=str(VIDEO_COUNT+int(self.get_children()[0].get_id())))
                item.res.append(res)
        return item

    def get_id(self):
        return self.id

    def get_name(self):
        return self.series.title

    def get_cover(self):
        return self.series.poster



class Episode(BackendItem):

    logCategory = 'smewt_media_store'

    def __init__(self, store, episode, id, parent_id):
        self.id = id
        self.episode = episode
        self.store = store

    def get_children(self,start=0,request_count=0):
        return []
        
    def get_child_count(self):
        return len(self.get_children())

    def get_item(self, parent_id = SERIES_CONTAINER_ID):
        item = DIDLLite.VideoItem(self.id, parent_id, self.episode.title)
        
        # add http resource
        for videoFile in self.episode.files:
          url = videoFile.filename
          mimetype = mimetypes.guess_type(url, strict=False)
          res = DIDLLite.Resource(url, 'http-get:*:%s:*' % mimetype)
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

        self.wmc_mapping.update({'4': lambda : self.get_by_id(SERIES_ALL_CONTAINER_ID),    # all series
                                 '7': lambda : self.get_by_id(MOVIES_ALL_CONTAINER_ID)
                                 })

        self.next_id = CONTAINER_COUNT
        self.series = None
        self.episodes = None
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "Smewt on %s" % self.server.coherence.hostname

        self.containers = {}
        self.containers[ROOT_CONTAINER_ID] = \
                Container( ROOT_CONTAINER_ID,-1, self.name)

        self.containers[SERIES_ALL_CONTAINER_ID] = \
                Container( SERIES_ALL_CONTAINER_ID,ROOT_CONTAINER_ID, 'All series',
                          children_callback=self.children_series,
                          store=self,play_container=False)
        self.containers[ROOT_CONTAINER_ID].add_child(self.containers[SERIES_ALL_CONTAINER_ID])

        louie.send('Coherence.UPnP.Backend.init_completed', None, backend=self)

    def get_by_id(self,id):

        self.info("looking for id %r", id)
        if isinstance(id, basestring):
            try:
                return self.containers[id]
            except:
                return None

        id = id.split('@',1)
        item_id = id[0]
        item_id = int(item_id)
        if item_id < TRACK_COUNT:
            try:
                item = self.containers[item_id]
            except KeyError:
                item = None
        else:
            item = Episode(self, (item_id - VIDEO_COUNT),None)

        return item

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
          
        self.warning("__init__ MediaStore initialized")

    def children_series(self, parent_id):
        series = []

        all_series = self.find_all(Series)
        for s in all_series:
          series.append(Series(self, s, serie.node.id, parent_id))
          
        return series