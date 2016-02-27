import sys
import os
import re
import urllib
import urllib2
from urlparse import urlparse
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
class yifyScraper(CommonScraper):
	broken = True
	
	def __init__(self):
		self._settings = {}
		self.service='yify'
		self.name = 'yify.tv'
		self.referrer = 'http://yify.tv'
		self.base_url = 'http://yify.tv'

	
	def search_tvshow(self, args):
		return []
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		html = self.request(uri)
		results = self.process_results(html)
		return results
	
	def process_results(self, html):
		results = []
		links = re.finditer("pic=([^&]+)", html)
		for link in links:
			url = "%s://%s" % (self.service, link.group(1))
			result = ScraperResult(self.service, self.service, url)
			result.quality = QUALITY.HD720
			results.append(result)
		return results

	def get_resolved_url(self, raw_url):
		resolved_url = ''
		uri = '/player/pk/pk/plugins/player_p2.php?url=' + raw_url
		json = self.request(uri, return_json=True)
		videos = []
		for link in json:
			if re.match('^video', link['type']):
				videos.append(link)
		if len(videos) == 1:
			resolved_url = videos[0]['url']
			return resolved_url
		else:
			self.search_results = []
			for v in videos:
				url = v['url']
				obj = urlparse(url)
				host_name =  re.sub('^www(.+?)\.', '', obj.hostname)
				result = ScraperResult(self.service, host_name, url)
				if v['width'] > 1280:
					result.quality = QUALITY.HD1080
				elif v['width'] == 1280:
					result.quality = QUALITY.HD720
				elif v['width'] == 640:
					result.quality = QUALITY.SD480
				else:
					result.quality = QUALITY.UNKNOWN	 
				self.search_results.append(result)
			resolved_url =  self.select_stream()			
		return resolved_url
		
	def prepair_query(self, media, *args, **kwards):
		title = args[0].replace(" ", "-").lower()
		try:	
			uri = "/watch-%s-%s-online-free-yify" % (title, args[1])
			urllib2.urlopen(self.base_url + uri)
		except:
			uri = "/watch-%s-online-free-yify" % title	
		return uri