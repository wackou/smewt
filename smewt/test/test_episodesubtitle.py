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
from smewt.base.subtitletask import SubtitleTask
from guessit import guess_episode_info
import chardet


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

            ep = guess_episode_info(video)

            series = ep.pop('series')

            g = MemoryObjectGraph()
            ep = g.Episode(series = g.Series(title = series), **ep)
            videofile = g.Media(filename = datafile(video), metadata = ep)

            subtask = SubtitleTask(ep, lang)
            sub = subtask.downloadEpisodeSubtitleText()

            self.assert_(self.subtitlesEqual(sub, open(datafile(subfile)).read()))


    def canonicalForm(self, encodedText):
        result = encodedText.replace('\r\n', '\n')
        encoding = chardet.detect(result)['encoding']

        # small hack as it seems chardet is not perfect :-)
        if encoding.lower().startswith('iso-8859'):
            encoding = 'iso-8859-1'

        return result.decode(encoding)

    def subtitlesEqual(self, sub1, sub2):
        sub1 = self.canonicalForm(sub1)
        sub2 = self.canonicalForm(sub2)

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

        open(subfile1, 'w').write(sub1.encode('utf-8'))
        open(subfile2, 'w').write(sub2.encode('utf-8'))
        import subprocess
        diffp = subprocess.Popen([ 'diff', subfile1, subfile2 ], stdout = subprocess.PIPE)
        diff, _ = diffp.communicate()


        # keep only the lines that are actual diff, not part of `diff` syntax
        realdiff = filter(lambda l: l and (l[0] == '<' or l[0] == '>'), diff.split('\n'))

        # remove those diffs that correspond to different indices of the sentences
        realdiff = filter(lambda l: len(l) > 6, realdiff)

        for i in realdiff:
            print i

        # 50 = completely arbitrary ;-)
        if len(realdiff) > 50:
            return False

        return True


suite = allTests(TestEpisodeSubtitle)


if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    shutdown()
