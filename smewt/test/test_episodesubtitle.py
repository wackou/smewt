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
from smewt.base.subtitletaskperiscope import SubtitleTaskPeriscope


def datafile(filename):
    return os.path.join(os.path.split(__file__)[0], 'test_episodesubtitle', filename)

class TestEpisodeSubtitle(TestCase):

    def setUp(self):
        ontology.reload_saved_ontology('media')

    def testPeriscopeSubtitle(self):
        for subdata in yaml.load(open(datafile('subsdata.yaml')).read()):
            video = subdata['video']
            lang =  subdata['language']
            subfile = subdata['result']

            from guessit import episode
            ep = episode.guess_episode_filename(video)

            series = ep.pop('series')

            g = MemoryObjectGraph()
            ep = g.Episode(series = g.Series(title = series), **ep)
            videofile = g.Media(filename = datafile(video), metadata = ep)

            subtask = SubtitleTaskPeriscope(ep, lang)
            sub = subtask.downloadSubtitleText()

            self.assert_(self.subtitlesEqual(sub, open(datafile(subfile)).read()))


    def subtitlesEqual(self, sub1, sub2):
        sub1 = sub1.replace('\r\n', '\n')
        sub2 = sub2.replace('\r\n', '\n')

        # why doesn't this work?
        #        import tempfile
        #        subfile1 = tempfile.NamedTemporaryFile()
        #        subfile1.write(sub1)
        #        subfile1.close()
        #        subfile2 = tempfile.NamedTemporaryFile()
        #        subfile2.write(sub2)
        #        subfile2.close()
        #
        #        # for python >= 2.7
        #        #subprocess.check_output
        #
        #        import subprocess
        #        subprocess.Popen([ 'diff', subfile1.name, subfile2.name ], stdout = subprocess.PIPE)

        subfile1 = '/tmp/sub1.srt'
        subfile2 = '/tmp/sub2.srt'

        open(subfile1, 'w').write(sub1)
        open(subfile2, 'w').write(sub2)
        import subprocess
        diffp = subprocess.Popen([ 'diff', subfile1, subfile2 ], stdout = subprocess.PIPE)
        diff, _ = diffp.communicate()

        os.remove(subfile1)
        os.remove(subfile2)


        # 19 = length of a diff chunk on a file with more than a 1000 lines (4+1+4 +1 +4+1+4)
        realdiff = filter(lambda l: len(l) > 19, diff.split('\n'))

        # 50 = completely arbitrary ;-)
        if len(realdiff) > 50:
            return False

        return True


suite = allTests(TestEpisodeSubtitle)


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    shutdown()
