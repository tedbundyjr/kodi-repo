import sys
import os
import re
import urllib
from urlparse import urlsplit
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult

class putlockerScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='putlocker'
		self.name = 'putlocker'
		self.referrer = 'http://putlocker.is'
		self.base_url = 'http://putlocker.is'

	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'], args['year'])
		if uri:
			html = self.request(uri, timeout=1)
			results = self.process_results(html)
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		if uri:
			html = self.request(uri, timeout=1.5)
			results = self.process_results(html)
		return results
	
	def process_results(self, html):
		results = []
		for match in re.finditer('<a[^>]+href="([^"]+)[^>]+>(Version \d+)<', html):
			url, version = match.groups()
			host_name = urlsplit(url).hostname.replace('embed.', '')
			if self.filter_host(host_name) and host_name != 'putlocker.is':
				url = "%s://%s" % (self.service, url)
				result = ScraperResult(self.service, host_name, url)
				result.quality = QUALITY.HIGH
				results.append(result)
		return results
	
		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			uri = '/search/advanced_search.php?'
			query = {"q": args[0], "from_year": args[3], "to_year": args[3], "section": 2}
			uri += urllib.urlencode(query)
			html = self.request(uri)
			if "Sorry, we couldn't find the movie that you were looking for." in html:
				return False
			r = re.search('Search Results For: "(.*?)</table>', html, re.DOTALL)
			if r:
				fragment = r.group(1)
				pattern = r'<a\s+href="([^"]+)"\s+title="([^"]+)'
				for match in re.finditer(pattern, fragment):
					url, title_year = match.groups('')
					url = url.replace('-tvshow-online-free-putlocker.html', '-tvshow-season-%s-episode-%s-online-free-putlocker.html' % (args[1], args[2]))
					uri = url.replace(self.base_url, '')
					return uri
			return False
		else:
			uri = '/search/advanced_search.php?'
			query = {"q": args[0], "from_year": args[1], "to_year": args[1], "section": 1}
			uri += urllib.urlencode(query)
			html = self.request(uri)
			if "Sorry, we couldn't find the movie that you were looking for." in html:
				return False
			r = re.search('Search Results For: "(.*?)</table>', html, re.DOTALL)
			if r:
				fragment = r.group(1)
				pattern = r'<a\s+href="([^"]+)"\s+title="([^"]+)'
				for match in re.finditer(pattern, fragment):
					url, title_year = match.groups('')
					uri = url.replace(self.base_url, '')
					return uri
			return False