import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
QUALITY_MAP = {"HD": QUALITY.HD, "DVD": QUALITY.SD480, "LQ DVD": QUALITY.LOW}
class solarmovieScraper(CommonScraper):
	broken = False
	def __init__(self):
		self._settings = {}
		self.service='solarmovie'
		self.name = 'solarmovie.is'
		self.timeout = 2
		self.referrer = 'https://www.solarmovie.is'
		self.base_url = 'https://www.solarmovie.is'
		self.ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
		self.USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
		self.headers = {'Accept-Language': 'en-US,en;q=0.8', 'Upgrade-Insecure-Requests': 1}
		
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'], args['year'])
		html = self.request(uri, headers=self.headers)
		results = self.process_results(html)
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		html = self.request(uri, headers=self.headers)
		results = self.process_results(html)
		return results
	
	def process_results(self, html):
		results = []
		pattern = '<tr id="link_(\d+?)"(.+?)</tr>'
		for link in re.finditer(pattern, html, re.DOTALL):
			id = link.group(1)
			html = link.group(2)
			host_name = re.search('<a href="/link/show/%s/">\s+(.+?)\s+</a>' % id, html, re.DOTALL)
			host_name = host_name.group(1)
			if self.filter_host(host_name):
				quality = re.search('<td class="qualityCell js-link-format" style="text-transform: uppercase;">\s+(.+?)\s+</td>', html, re.DOTALL)
				quality = quality.group(1).upper()
				url = "%s:///link/play/%s/" % (self.service, id)
				result = ScraperResult(self.service, host_name, url)
				if quality in QUALITY_MAP.keys():
					result.quality = QUALITY_MAP[quality]
				else:
					result.quality = QUALITY.UNKNOWN
				results.append(result)
		return results
	
	def get_resolved_url(self, uri):
		html = self.request(uri, headers=self.headers)
		iframe = re.search('<iframe (.+?)</iframe>', html, re.IGNORECASE|re.DOTALL)
		if iframe:
			html = iframe.group(1)
			raw_url = re.search('src="(.+?)"', html, re.DOTALL|re.IGNORECASE)
			if raw_url:
				return self.do_urlresolver(raw_url)
		return None

		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			showname = args[0].replace(' (US)', '')
			showname = showname.lower().replace(" ", "-")
			season = args[1]
			episode = args[2]
			year = args[3]
			uri = "/tv/%s-%s/season-%s/episode-%s/" % (showname, year, season, episode)
			return uri
		else:
			title = args[0].lower().replace(" ", "-")
			year = args[1]
			uri = "/watch-%s-%s.html" % (title, year)
			return uri