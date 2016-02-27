import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
class vidicsScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='vidics'
		self.name = 'vidics.ch'
		self.referrer = 'http://www.vidics.ch'
		self.base_url = 'http://www.vidics.ch'
		self.timeout = 2
	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'])
		soup = self.request(uri, return_soup=True)
		results = self.process_results(soup)
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'])
		soup = self.request(uri, return_soup=True)
		results = self.process_results(soup)
		return results
	
	def process_results(self, soup):
		results = []
		links = soup.findAll('a', {"rel": "nofollow", "target": "_blank"})
		for link in links:
			host_name = link.string.lower()
			if self.filter_host(host_name):
				url = "%s://%s" % (self.service, link['href'])
				result = ScraperResult(self.service, host_name, url)
				result.quality = QUALITY.UNKNOWN
				results.append(result)	
		return results
	
	def get_resolved_url(self, raw_url):
		raw_url = self.get_redirect(raw_url)
		return self.do_urlresolver(raw_url)
		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			showname = args[0].lower().replace(" ", "_")
			season = args[1]
			episode = args[2]
			uri = "/Serie/%s-Season-%s-Episode-%s" % (showname, season, episode)
		else:
			import string
			title = string.capwords(args[0]).replace(" ", "_")		
			uri = "/Film/%s" % title
		return uri