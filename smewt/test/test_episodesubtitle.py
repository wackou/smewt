#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Smewt - A smart collection manager
# Copyright (c) 2008 Nicolas Wack <wackou@gmail.com>
#
# Smewt is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# Smewt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from smewttest import *
from smewt.media.subtitle.subtitle_tvsubtitles_provider import TVSubtitlesProvider


def datafile(filename):
    return os.path.join(os.path.split(__file__)[0], 'test_episodesubtitle', filename)

class TestEpisodeSubtitle(TestCase):

    def setUp(self):
        ontology.reload_saved_ontology('media')

    def testSingleSubtitle(self):
        for subdata in yaml.load(open(datafile('subsdata.yaml')).read()):
            query = MemoryObjectGraph()
            resultFile = subdata['result']
            del subdata['result']

            language = subdata['language']
            del subdata['language']

            s = query.Series(title = subdata['series'])
            del subdata['series']

            ep = query.Episode(series = s, **subdata)

            subprovider = TVSubtitlesProvider()

            self.assert_(subprovider.canHandle(ep))

            available = subprovider.getAvailableSubtitles(ep).find_all(Subtitle, language = language)
            self.assert_(len(available) >= 1)

            sub = available[0]
            # FIXME: should implement hint with the filename...
            if '720p' in available[0].source and len(available) > 1:
                sub = available[1]

            sub = subprovider.getSubtitle(sub)
            self.assertEqual(open(datafile(resultFile)).read(), sub.replace('\r\n', '\n'))



suite = allTests(TestEpisodeSubtitle)


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    shutdown()
