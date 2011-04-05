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
from smewt.media.movie.movieobject import Movie
from smewt.base.utils import tolist

from coherence import __version_info__

from coherence.upnp.core import DIDLLite
from coherence.upnp.core import utils

from coherence.backend import BackendItem, BackendStore

from coherenceviews import *

ROOT_CONTAINER_ID = 0
VIDEO_CONTAINER = 100
SERIES_CONTAINER_ID = 101
MOVIES_CONTAINER_ID = 102

CONTAINER_COUNT = 10000

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
        self.only_available = kwargs.get("only_available", True)
        self.series = None
        self.episodes = None
        
        self.next_id = 0
        self.items = {}
        self.ids = {}
        
        try:
            self.name = kwargs['name']
        except KeyError:
            self.name = "Smewt on %s" % self.server.coherence.hostname

        self.root_container = Container(self, self.name, -1)
        
        self.add_container('All series', lambda pid: advSeries(self, self.smewt_db, parent_id=pid))
        self.add_container('All movies', lambda pid: allMovies(self, self.smewt_db, parent_id=pid))
        self.add_container('Movies by genre', lambda pid: moviesByProperty(self, self.smewt_db, 'genres', parent_id=pid))
        self.add_container('Movies by year', lambda pid: moviesByProperty(self, self.smewt_db, 'year', getProperty = lambda x: [x.get('year', None)], parent_id=pid))
        self.add_container('Movies by director', lambda pid: moviesByProperty(self, self.smewt_db, 'director', parent_id=pid))
        self.add_container('Movies by cast', lambda pid: moviesByProperty(self, self.smewt_db, 'cast', getProperty = lambda x: [act.split('--')[0] for act in x.get('cast', [])], parent_id=pid))
        
        louie.send('Coherence.UPnP.Backend.init_completed', None, backend=self)

    def add_container(self, name, childrenMethod):
        cont = Container(self, name, self.root_container.get_id())
        cont.add_children(childrenMethod(cont.id))
        self.root_container.add_child(cont)

    def get_by_id(self,id):
        self.info("looking for id %r", id)
        if '@' in id:
          id = id.split('@')[0]
        return self.items[int(id)]
        
    def new_item(self, item):
        #FIXME: make a proper mapping between pygoo and upnp ids
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
