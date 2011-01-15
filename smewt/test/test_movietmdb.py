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
import glob


tests = '''
/data/Movies/Fear and Loathing in Las Vegas (1998)/Fear.and.Loathing.in.Las.Vegas.720p.HDDVD.DTS.x264-ESiR.mkv:
    title: Fear and Loathing in Las Vegas
    year: 1998

/data/Movies/El Dia de la Bestia (1995)/El.dia.de.la.bestia.DVDrip.Spanish.DivX.by.Artik[SEDG].avi:
    title: El día de la bestia
    year: 1995

/data/Movies/Blade Runner (1982)/Blade.Runner.(1982).(Director's.Cut).CD1.DVDRip.XviD.AC3-WAF.avi:
    title: Blade Runner
    year: 1982

/data/Movies/Dark City (1998)/Dark.City.(1998).DC.BDRip.720p.DTS.X264-CHD.mkv:
    title: Dark City
    year: 1998

/data/Movies/Sin City (BluRay) (2005)/Sin.City.2005.BDRip.720p.x264.AC3-SEPTiC.mkv:
    title: Sin City
    year: 2005

"[XCT].Le.Prestige.(The.Prestige).DVDRip.[x264.HP.He-Aac.{Fr-Eng}.St{Fr-Eng}.Chaps].mkv":
    title: The Prestige
    year: 2006

Butch Cassidy and the Sundance Kid (1969)/Butch_Cassidy_And_The_Sundance_Kid_(1969).avi:
    title: Butch Cassidy and the Sundance Kid
    year: 1969

Brazil (1985)/Brazil_Criterion_Edition_(1985).CD1.avi:
    title: Brazil
    year: 1985

Waking Life (2001)/Waking.Life.2001.DVDRip.{x264-Hp+AAC-He}{Eng}{Sub.Fr}{Chapitres}.mkv:
    title: Waking Life
    year: 2001

Futurama - Bender's Game (2008)/Futurama.Benders.Game.2008.DVDRiP.XViD-DOMiNO.avi:
    title: "Futurama: Bender's Game"
    year: 2008

American Gangster (2007)/American Gangster[2007][Unrated Edition]DvDrip[Eng]-FXG.avi:
    title: American Gangster
    year: 2007

Airbag (1997)/Airbag_Spanish_DivX_DVDRip_by_Sir_Blade.(576x240).avi:
    title: Airbag
    year: 1997

Futurama - Into The Wild Green Yonder (2009)/Futurama.Into.The.Wild.Green.Yonder.720p.Bluray.x264-ANiHLS.mkv:
    title: "Futurama: Into the Wild Green Yonder"
    year: 2009

Battle Royale (2000)/Battle.Royale.(Batoru.Rowaiaru).(2000).(Special.Edition).CD1of2.DVDRiP.XviD-[ZeaL].avi:
    title: Battle Royale
    year: 2000

Dude Where's My Car? (2000)/Dude.Where's.My.Car.(2000).BDRip.720p.DTS.X264-HiS@SiLUHD.mkv:
    title: Dude, Where’s My Car?
    year: 2000

Comme une Image (2004)/Comme.Une.Image.FRENCH.DVDRiP.XViD-NTK.par-www.divx-overnet.com.avi:
    title: Comme une image
    year: 2004

'''


failtests = '''
Chat noir, chat blanc (1998)/Chat noir, Chat blanc - Emir Kusturica (VO - VF - sub FR - Chapters).mkv:
    title: Chat noir, chat blanc
    year: 1998

Batman Begins (2005)/Batman Begins.2005.HDDVDRIP.720p.AC3.5.1.x264-Audiofixed.mkv:
    title: Batman Begins
    year: 2005

El Bosque Animado (1987)/El.Bosque.Animado.[Jose.Luis.Cuerda.1987].[Xvid-Dvdrip-720x432].avi:
    title: El bosque animado
    year: 1987

'''


class TestMovieTMDB(TestCase):

    def setUp(self):
        ontology.reload_saved_ontology('media')

    def testSimple(self):
        data = yaml.load(tests)

        for filename, md in data.items():
            print 'testing', filename
            query = MemoryObjectGraph()
            query.Media(filename = unicode(filename))

            schain = SolvingChain(MovieFilename(), MovieTMDB())
            result = schain.solve(query).find_all(Movie)

            self.assertEqual(len(result), 1, 'Solver coudn\'t solve anything...')
            result = result[0]

            for key, value in md.items():
                self.assertEqual(result.get(key), value)

            from smewt.base import cache
            cache.save('/tmp/smewt.cache')



suite = allTests(TestMovieTMDB)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
    smewt.shutdown()
