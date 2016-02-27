import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult


class dizilabScraper(CommonScraper):
	def __init__(self):
		self.service='dizilab'
		self.name = 'dizilab.com'
		self.referrer = 'http://dizilab.com'
		self.base_url = 'http://dizilab.com'
		self.timeout = 2
	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'])
		html = self.request(uri)
		results = self.process_results(html)
		return results
	
	def search_movie(self, args):
		return []
	
	def process_results(self, html):
		results = []
		for match in re.finditer('{\s*file\s*:\s*"([^"]+)', html):
			stream_url = match.group(1)
			if 'dizlab' not in stream_url.lower():
				url = "%s://%s" % (self.service, stream_url)
				result = ScraperResult(self.service, 'gvideo', url)
				result.quality = self.test_gv_quality(stream_url)
				results.append(result)
		return results
	
	def get_resolved_url(self, raw_url):
		resolved_url = raw_url
		return resolved_url
		
	def prepair_query(self, media, *args, **kwards):
		showname = args[0].lower().replace(" ", "_")
		season = args[1]
		episode = args[2]
		uri = "/%s/sezon-%s/bolum-%s" % (showname, season, episode)
		return uri
