## dvrasp 15.4.09 v.001
## Sources :
##  - http://code.google.com/p/arturo/source/browse/trunk/plugins/net/tvsubtitles.py
##  - http://www.gtk-apps.org/CONTENT/content-files/90184-download_tvsubtitles.net.py

import logging

import zipfile, os, urllib2
import os, re, BeautifulSoup, urllib
import guessit
from lxml import etree

log = logging.getLogger(__name__)

showNum = {
"24":38,
"30 rock":46,
"90210":244,
"afterlife":200,
"alias":5,
"aliens in america":119,
"ally mcbeal":158,
"american dad":138,
"andromeda":60,
"andy barker: p.i.":49,
"angel":98,
"army wives":242,
"arrested development":161,
"ashes to ashes":151,
"avatar: the last airbender":125,
"back to you":183,
"band of brothers":143,
"battlestar galactica":42,
"big day":237,
"big love":88,
"big shots":137,
"bionic woman":113,
"black adder":176,
"black books":175,
"blade":177,
"blood ties":140,
"bonekickers":227,
"bones":59,
"boston legal":77,
"breaking bad":133,
"brotherhood":210,
"brothers &amp; sisters":66,
"buffy the vampire slayer":99,
"burn notice":50,
"californication":103,
"carnivale":170,
"carpoolers":146,
"cashmere mafia":129,
"charmed":87,
"chuck":111,
"city of vice":257,
"cold case":95,
"criminal minds":106,
"csi":27,
"csi miami":51,
"csi ny":52,
"curb your enthusiasm":69,
"damages":124,
"dark angel":131,
"day break":6,
"dead like me":13,
"deadwood":48,
"desperate housewives":29,
"dexter":55,
"dirt":145,
"dirty sexy money":118,
"do not disturb":252,
"doctor who":141,
"dollhouse" : 448,
"drive":97,
"eli stone":149,
"entourage":25,
"er (e.r.)":39,
"eureka":43,
"everybody hates chris":81,
"everybody loves raymond":86,
"exes &amp; ohs":199,
"extras":142,
"fallen":101,
"family guy":62,
"farscape":92,
"fawlty towers":178,
"fear itself":201,
"felicity":217,
"firefly":84,
"flash gordon":134,
"flashpoint":221,
"friday night lights":57,
"friends":65,
"fringe":204,
"futurama":126,
"generation kill":223,
"ghost whisperer":14,
"gilmore girls":28,
"gossip girl":114,
"greek":102,
"grey's anatomy":7,
"hank":538,
"heroes":8,
"hidden palms":44,
"hotel babylon":164,
"house m.d.":9,
"how i met your mother":110,
"hustle":160,
"in justice":144,
"in plain sight":198,
"in treatment":139,
"into the west":256,
"invasion":184,
"it's always sunny in philadelphia":243,
"jeeves and wooster":180,
"jekyll":61,
"jericho":37,
"joey":83,
"john adams":155,
"john from cincinnati":79,
"journeyman":108,
"k-ville":107,
"keeping up appearances":167,
"knight rider":163,
"kyle xy":10,
"lab rats":233,
"las vegas":75,
"life":109,
"life is wild":120,
"life on mars (uk)":90,
"lipstick jungle":150,
"lost":3,
"lost in austen":254,
"lucky louie":238,
"mad men":136,
"meadowlands":45,
"medium":12,
"melrose place":189,
"men in trees":127,
"miami vice":208,
"monk":85,
"moonlight":117,
"my name is earl":15,
"ncis":30,
"new amsterdam":153,
"nip/tuck":23,
"northern exposure":241,
"numb3rs":11,
"october road":132,
"one tree hill":16,
"over there":93,
"oz":36,
"painkiller jane":35,
"pepper dennis":82,
"police squad":190,
"popetown":179,
"pretender":245,
"primeval":130,
"prison break":2,
"private practice":115,
"privileged":248,
"project runway":226,
"psych":17,
"pushing daisies":116,
"queer as folk":229,
"reaper":112,
"regenesis":152,
"rescue me":91,
"robin hood":121,
"rome":63,
"roswell":159,
"samantha who?":123,
"samurai girl":255,
"saving grace":104,
"scrubs":26,
"secret diary of a call girl":196,
"seinfeld":89,
"sex and the city":68,
"shameless":193,
"shark":24,
"sharpe":186,
"six feet under":94,
"skins":147,
"smallville":1,
"sophie":203,
"south park":71,
"spooks":148,
"standoff":70,
"stargate atlantis":54,
"stargate sg-1":53,
"studio 60 on the sunset strip":33,
"supernatural":19,
"swingtown":202,
"taken":67,
"tell me you love me":182,
"terminator: the sarah connor chronicles":128,
"the 4400":20,
"the andromeda strain":181,
"the big bang theory":154,
"the black donnellys":216,
"the cleaner":225,
"the closer":78,
"the dead zone":31,
"the dresden files":64,
"the fixer":213,
"the inbetweeners":197,
"the it crowd":185,
"the l word":74,
"the middleman":222,
"the net":174,
"the no. 1 ladies' detective agency":162,
"the o.c. (the oc)":21,
"the office":58,
"the outer limits":211,
"the riches":156,
"the secret life of the american teenager":218,
"the shield":40,
"the simple life":234,
"the simpsons":32,
"the sopranos":18,
"the tudors":76,
"the unit":47,
"the war at home":80,
"the west wing":168,
"the wire":72,
"the x-files":100,
"threshold":96,
"til death":171,
"tin man":122,
"top gear":232,
"torchwood":135,
"traveler":41,
"tripping the rift":188,
"tru calling":4,
"true blood":205,
"twin peaks":169,
"two and a half men":56,
"ugly betty":34,
"ultimate force":194,
"unhitched":157,
"veronica mars":22,
"weeds":73,
"will & grace":172,
"without a trace":105,
"women's murder club":166,
"wonderfalls":165
 }


def between(s, left, right):
    return s.split(left)[1].split(right)[0]

def simpleMatch(string, regexp):
    try:
        return re.compile(regexp).search(string).groups()[0]
    except IndexError:
        raise Exception("'%s' Does not match regexp '%s'" % (string, regexp))

def levenshtein(a, b):
    if not a: return len(b)
    if not b: return len(a)

    m = len(a)
    n = len(b)
    d = []
    for i in range(m+1):
        d.append([0] * (n+1))

    for i in range(m+1):
        d[i][0] = i

    for j in range(n+1):
        d[0][j] = j

    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]:
                cost = 0
            else:
                cost = 1

            d[i][j] = min(d[i-1][j] + 1,     # deletion
                          d[i][j-1] + 1,     # insertion
                          d[i-1][j-1] + cost # substitution
                          )

    return d[m][n]


import SubtitleDatabase

class TvSubtitles(SubtitleDatabase.SubtitleDB):
	url = "http://www.tvsubtitles.net"
	site_name = "TvSubtitles"

	URL_SHOW_PATTERN = "http://www.tvsubtitles.net/tvshow-%d.html"
	URL_SEASON_PATTERN = "http://www.tvsubtitles.net/tvshow-%d-%d.html"
        URL_EPISODE_PATTERN = "http://www.tvsubtitles.net/episode-%d.html"
        URL_SUBTITLE_PATTERN = "http://www.tvsubtitles.net/download-%d.html"

	def __init__(self):
		super(TvSubtitles, self).__init__({}) #"en":'en', "fr":'fr'})## TODO ??
		self.host = TvSubtitles.url

        #@cachedmethod
        # NOTE: uses lxml at the moment
        def getLikelyShowUrl(self, name):
                data = urllib.urlencode({ 'q': name })
                html = etree.HTML(urllib2.urlopen(self.url + '/search.php', data).read())
                matches = [ s.find('a') for s in html.findall(".//div[@style='']") ]

                # add baseUrl and remove year information
                result = []
                for match in matches:
                        seriesID = int(match.get('href').split('-')[1].split('.')[0]) # remove potential season number
                        seriesUrl = self.url + '/tvshow-%d.html' % seriesID
                        title = match.text
                        try:
                                idx = title.find('(') - 1
                                title = title[:idx]
                        except: pass

                        result.append({ 'title': title, 'url': seriesUrl })

                if not matches:
                        raise SmewtException("Couldn't find any matching series for '%s'" % name)

                return result


        #@cachedmethod
        def getShowId(self, name):
                name = name.lower()
                showId = showNum.get(name, None)
                if showId:
                        log.debug("Show ID cached value for %s: %d" % (name, showId))
                        return showId


                # get most likely one if more than one found
                # FIXME: this hides another potential bug which is that tvsubtitles returns a lot of
                # false positives that it doesn't return when using from a "normal" webbrowser...
                urls = [ (levenshtein(s['title'].lower(), name), s) for s in self.getLikelyShowUrl(name) ]
                url = sorted(urls)[0][1]['url']
                result = int(simpleMatch(url, 'tvshow-(.*?).html'))

                log.debug('Found show ID for %s: %d' % (name, result))
                return result


        #@cachedmethod
        def getEpisodeId(self, show, season, episode):
                showID = self.getShowId(show)
                seasonHtml = urllib2.urlopen(self.URL_SEASON_PATTERN % (showID, season)).read()
                try:
                        episodeRowHtml = between(seasonHtml, '%dx%02d' % (season, episode), '</tr>')
                except IndexError:
                        raise Exception("Season %d Episode %d unavailable for series '%s'" % (season, episode, series))

                result = int(simpleMatch(episodeRowHtml, 'episode-(.*?).html'))

                log.debug('Found episode ID for %s %dx%2d: %d' % (show, season, episode, result))
                return result


        # NOTE: uses lxml at the moment
        def query(self, show, season, episode, teams, langs):
                episodeId = self.getEpisodeId(show, season, episode)

                episodeURL = self.URL_EPISODE_PATTERN % episodeId
                episodeHtml = urllib2.urlopen(episodeURL).read()

                episodeHtml = between(episodeHtml, '<b>Subtitles for this episode:</b>', '<br clear=all>')
                ehtml = etree.HTML(episodeHtml)

                links = []
                for slink, sub in zip(ehtml.findall('.//a'),
                                      ehtml.findall(".//div[@class='subtitlen']")):

                        tvsubid = int(between(slink.get('href'), '-', '.'))

                        links.append(dict(lang = simpleMatch(sub.find('.//img').get('src'), 'flags/(.*?).gif'),
                                          link = self.URL_SUBTITLE_PATTERN % tvsubid,
                                          forceType = 'zip',
                                          title = (sub.find('.//h5').find('img').tail or '').strip(),
                                          source = (sub.find(".//p[@title='rip']").find('img').tail or '').strip(),
                                          release = (sub.find(".//p[@title='release']").find('img').tail or '').strip()))


                # keep only the ones with our desired languages
                links = [ link for link in links if link['lang'] in langs ]

                # TODO: if any, only keep the ones with matching "teams"

                return links


	def process(self, filename, langs):
		''' main method to call on the plugin, pass the filename and the wished
		languages and it will query TvSubtitles.net '''

                guessedData = guessit.guess_video_info(filename)
                log.debug(filename)

		if guessedData['type'] == 'episode':
			subs = self.query(guessedData['series'], guessedData['season'], guessedData['episodeNumber'],
                                          guessedData.get('releaseGroup', []), langs)
			return subs
		else:
			return []
