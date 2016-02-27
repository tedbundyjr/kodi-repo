import sys
import os
import re
import urllib
from urlparse import urlparse
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
QUALITY_MAP = {"HD": QUALITY.HD, "DVD": QUALITY.SD480, "CAM": QUALITY.LOW, "TS": QUALITY.LOW}
class losmoviesScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='losmovies'
		self.name = 'losmovies.is'
		self.referrer = 'http://losmovies.ws'
		self.base_url = 'http://losmovies.ws'
		self.timeout = 3
	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['year'])
		if uri:
			html = self.request(uri)
			results = self.process_tvshow_results(html, args['imdb_id'], args['season'], args['episode'])
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		html = self.request(uri)
		results = self.process_movie_results(html, args['imdb_id'])
		return results
	
	def process_movie_results(self, html, imdb_id):
		results = []
		match = re.search('imdb\.com/title/(tt\d+?)"', html)
		if match:
			if match.group(1) != imdb_id: return results
		for link in re.finditer('<tr class="linkTr">(.+?)</tr>', html, re.DOTALL):
			html = link.group(1)
			url = re.search('linkHiddenUrl" data-width="\d+" data-height="\d+">(.+?)</td>', html).group(1)
			obj = urlparse(url)
			host_name =  re.sub('^(www\.|embed\.)*', '', obj.hostname)
			filter = False
			if self.domains is not None:
				filter = True
			if filter == False or (host_name in self.domains and filter == True):
				url = "%s://%s" % (self.service, url)
				quality = re.search('linkQuality([A-Z]+?)"', html).group(1)
				result = ScraperResult(self.service, host_name, url)
				if quality in QUALITY_MAP.keys():
					result.quality = QUALITY_MAP[quality]
				else:
					result.quality = QUALITY.UNKNOWN
				results.append(result)
		return results		
	
	def process_tvshow_results(self, html, imdb_id, season, episode):
		results = []
		match = re.search('imdb\.com/title/(tt\d+?)"', html)
		if match:
			if match.group(1) != imdb_id: return results
		pattern = 'Season %s Serie %s(.*?)</table>' % (season, episode)
		match = re.search(pattern, html, re.DOTALL)
		html = match.group(1)
		
		for link in re.finditer('<tr class="linkTr">(.+?)</tr>', html, re.DOTALL):
			html = link.group(1)
			url = re.search('linkHiddenUrl" data-width="\d+" data-height="\d+">(.+?)</td>', html).group(1)
			obj = urlparse(url)
			host_name =  re.sub('^(www\.|embed\.)*', '', obj.hostname)
			if self.filter_host(host_name):
				url = "%s://%s" % (self.service, url)
				quality = re.search('linkQuality([A-Z]+?)"', html).group(1)
				result = ScraperResult(self.service, host_name, url)
				if quality in QUALITY_MAP.keys():
					result.quality = QUALITY_MAP[quality]
				else:
					result.quality = QUALITY.UNKNOWN
				results.append(result)
		return results
	

		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			search_uri = 'search'
			html = self.request(search_uri, query={"type": "movies", "q": args[0]})
			pattern = 'class="movieQuality[^>]+>\s*(.*?)\s*<div\s+class="movieInfo".*?showRowImage">\s*<a\s+href="([^"]+).*?<h4[^>]+>([^<]+)'
			for match in re.finditer(pattern, html, re.DOTALL):
				match_type, uri, title = match.groups('')
				
				if 'movieTV' not in match_type:
					continue
				r = re.search('(\d{4})$', uri)
				if r:
					match_year = r.group(1)
				else:
					match_year = ''
				if args[1] == match_year:
					return uri
				pattern = '/watch-online-%s$' % args[0].lower().replace(" ", "-")
				match = re.search(pattern, uri)
				if match: 
					return uri
			
			return False	
		else:
			search_uri = 'search'
			html = self.request(search_uri, query={"type": "movies", "q": args[0]})
			pattern = 'class="movieQuality[^>]+>\s*(.*?)\s*<div\s+class="movieInfo".*?showRowImage">\s*<a\s+href="([^"]+).*?<h4[^>]+>([^<]+)'
			for match in re.finditer(pattern, html, re.DOTALL):
				match_type, uri, title = match.groups('')
				if 'movieTV' in match_type:
					continue
				r = re.search('(\d{4})$', uri)
				if r:
					match_year = r.group(1)
				else:
					match_year = ''
				if args[1] == match_year:
					return uri
				pattern = '/watch-online-%s$' % args[0].lower().replace(" ", "-")
				match = re.search(pattern, uri)
				if match: 
					return uri
			return False