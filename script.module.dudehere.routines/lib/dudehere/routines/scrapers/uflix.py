import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
class uflixScraper(CommonScraper):
	broken = True
	
	def __init__(self):
		self._settings = {}
		self.service='uflix'
		self.name = 'uflix.me'
		self.referrer = 'http://www.uflix.ws'
		self.base_url = 'http://www.uflix.ws'

	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'])
		html = self.request(uri)
		results = self.process_results(html)
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		html = self.request(uri)
		results = self.process_results(html)
		return results
	
	def process_results(self, html):
		results = []
		if re.search('Quality:  <img src="http://uflix.me/themes/Blu-Ray.gif"', html):
			quality = QUALITY.SD480
		else:
			quality = QUALITY.UNKNOWN
		
		pattern = 'url=([^&]+)&domain=([^&"]+)'
		print html
		for link in re.finditer(pattern, html):
			url, host_name = link.groups()
			url = url.decode('base-64')
			host_name = host_name.decode('base-64').lower()
			if self.filter_host(host_name):
				url = "%s://%s" % (self.service, url)
				result = ScraperResult(self.service, host_name, url)
				result.quality = quality
				results.append(result)	
		return results
	

		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			showname = args[0].lower().replace(" ", "-")
			season = args[1]
			episode = args[2]
			uri = "/show/%s/season/%s/episode/%s" % (showname, season, episode)
		else:
			query = {"menu": "search", "advsearch": 1, "title": args[0], "year": args[1], "submit": ""}
			uri = "index.php"
			html = self.request(uri, query=query)
			pattern = 'href="%s(.+?)" title="Watch %s Online' % (self.base_url, args[0])
			match = re.search(pattern, html)
			if match:
				return match.group(1)