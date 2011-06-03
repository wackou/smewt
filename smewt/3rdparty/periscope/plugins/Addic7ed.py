# -*- coding: utf-8 -*-

#   This file is part of periscope.
#
#    periscope is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    periscope is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with periscope; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import zipfile, os, urllib2, urllib, logging, traceback, httplib, re, socket
from BeautifulSoup import BeautifulSoup
import guessit

import SubtitleDatabase

log = logging.getLogger(__name__)

LANGUAGES = {u"English" : "en",
			 u"English (US)" : "en",
			 u"English (UK)" : "en",
			 u"Italian" : "it",
			 u"Portuguese" : "pt",
			 u"Portuguese (Brazilian)" : "pt-br",
			 u"Romanian" : "ro",
			 u"Español (Latinoamérica)" : "es",
			 u"Español (España)" : "es",
			 u"Spanish (Latin America)" : "es",
			 u"Español" : "es",
			 u"Spanish" : "es",
			 u"Spanish (Spain)" : "es",
			 u"French" : "fr",
			 u"Greek" : "el",
			 u"Arabic" : "ar",
			 u"German" : "de",
			 u"Croatian" : "hr",
			 u"Indonesian" : "id",
			 u"Hebrew" : "he",
			 u"Russian" : "ru",
			 u"Turkish" : "tr",
			 u"Swedish" : "se",
			 u"Czech" : "cs",
			 u"Dutch" : "nl",
			 u"Hungarian" : "hu",
			 u"Norwegian" : "no",
			 u"Polish" : "pl",
			 u"Persian" : "fa"}

class Addic7ed(SubtitleDatabase.SubtitleDB):
	url = "http://www.addic7ed.com"
	site_name = "Addic7ed"

	def __init__(self):
		super(Addic7ed, self).__init__(langs=None,revertlangs=LANGUAGES)
		#http://www.addic7ed.com/serie/Smallville/9/11/Absolute_Justice
		self.host = "http://www.addic7ed.com"
		self.release_pattern = re.compile(" \nVersion (.+), ([0-9]+).([0-9])+ MBs")


	def process(self, filepath, langs):
		''' main method to call on the plugin, pass the filename and the wished
		languages and it will query the subtitles source '''
                guessedData = guessit.guess_video_info(filepath)
                if guessedData['type'] == 'episode':
                        team = [ guessedData['releaseGroup'].lower() ] if 'releaseGroup' in guessedData else []
                        return self.query(guessedData['series'], guessedData['season'], guessedData['episodeNumber'], team, langs)
                else:
                        return []


	def query(self, name, season, episode, teams, langs=None):
		''' makes a query and returns info (link, lang) about found subtitles'''
		sublinks = []
		name = name.lower().replace(" ", "_")
		searchurl = "%s/serie/%s/%s/%s/%s" %(self.host, name, season, episode, name)
                log.debug("dl'ing %s" % searchurl)
                content = self.downloadText(searchurl, timeout = 5)
                if not content:
                        return sublinks


                # HTML bug in addic7ed that prevents BeautifulSoup 3.1 from correctly parsing the html
                # BeautifulSoup 3.2 doesn't have this problem, though
                content = re.sub(r'"true"/ onclick="saveWatched(\([0-9,]*\));" >',
                                 r'"true" onclick="saveWatched\1;" />',
                                 content)

		soup = BeautifulSoup(content)
                log.debug('Found %d potential subs' % len(soup("td", {"class":"NewsTitle", "colspan" : "3"})))
		for subs in soup("td", {"class":"NewsTitle", "colspan" : "3"}):
			if not self.release_pattern.match(str(subs.contents[1])):
				continue

			subteams = self.release_pattern.match(str(subs.contents[1])).groups()[0].lower()

			# Addic7ed only takes the real team into account
			fteams = []
			for team in teams:
				fteams += team.split("-")
			teams = set(fteams)
			subteams = self.listTeams([subteams], [".", "_", " "])

			log.debug("[Addic7ed] Team from website: %s - from file: %s - match = %s" % (subteams, teams, subteams.issubset(teams)))
			langs_html = subs.findNext("td", {"class" : "language"})
			lang = self.getLG(langs_html.contents[0].strip().replace('&nbsp;', ''))
			#log.debug("[Addic7ed] Language : %s - lang : %s" %(langs_html, lang))

			statusTD = langs_html.findNext("td")
			status = statusTD.find("b").string.strip()

			# take the last one (most updated if it exists)
			links = statusTD.findNext("td").findAll("a")
			link = "%s%s"%(self.host,links[len(links)-1]["href"])

			log.debug("%s - match : %s - lang : %s" %(status == "Completed", subteams.issubset(teams), (not langs or lang in langs)))
			if status == "Completed" and subteams.issubset(teams) and (not langs or lang in langs) :
				result = {}
				result["release"] = "%s.S%.2dE%.2d.%s" %(name.replace("_", ".").title(), int(season), int(episode), '.'.join(subteams)
)
				result["lang"] = lang
				result["link"] = link
				result["page"] = searchurl
                                result["forceType"] = "srt"
				sublinks.append(result)
		return sublinks

	def listTeams(self, subteams, separators):
		teams = []
		for sep in separators:
			subteams = self.splitTeam(subteams, sep)
		#log.debug(subteams)
		return set(subteams)

	def splitTeam(self, subteams, sep):
		teams = []
		for t in subteams:
			teams += t.split(sep)
		return teams

