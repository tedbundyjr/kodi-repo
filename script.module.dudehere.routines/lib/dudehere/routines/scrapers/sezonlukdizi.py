#!/usr/bin/python
# -*- coding: utf-8 -*-
PYTHONIOENCODING="UTF-8"
import sys
import os
import re
import json
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult



class sezonlukdiziScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='sezonlukdizi'
		self.name = 'sezonlukdizi'
		self.referrer = 'http://sezonlukdizi.com/'
		self.base_url = 'http://sezonlukdizi.com/'
		self.timeout = 5

	
	def search_tvshow(self, args):
		results = []
		url = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'],args['year'])
		if url:
			html = self.request(url, timeout=5, append_base=True)
			results = self.process_results(html)
		return results
	
	def search_movie(self, args):
		return []
	
	def process_results(self, html):
		results = []
		for match in re.finditer('"?file"?\s*:\s*"([^"]+)"\s*,\s*"?label"?\s*:\s*"(\d+)p?"', html):
			stream_url, height = match.groups()
			stream_url = stream_url.replace('\\&', '&').replace('\\/', '/')
			if 'v.asp' in stream_url and 'ok.ru' not in html:
				redirect = self.request(stream_url, get_redirect=True, append_base=False)
				url = "%s://%s" % (self.service, stream_url)
				if 'google' in redirect or '' in redirect:
					host_name = 'gvideo'
					quality = self.test_gv_quality(redirect)
				else:
					host_name = self.service
					quality = self.test_height_quality(height)
				result = ScraperResult(self.service, host_name, url)
				result.quality = self.test_gv_quality(redirect)
				results.append(result)
		return results
	



	def get_resolved_url(self, raw_url):
		resolved_url = raw_url
		return resolved_url
		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			uri = '/%s/%s-sezon-%s-bolum.html' % (args[0].replace(' ', '-'),args[1], args[2])
			html = self.request(uri)
			match1 = re.search('var\s+video_id\s*=\s*"([^"]+)', html)
			match2 = re.search('var\s+part_name\s*=\s*"([^"]+)', html)
			if match1 and match2:
				headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': self.base_url + uri}
				video_id = match1.group(1)
				part_name = match2.group(1)
				uri = '/service/get_video_part'
				data = {'video_id': video_id, 'part_name': part_name, 'page': 0}
				result = self.request(uri, data, headers=headers, return_json=True)
				if 'part_count' in result:
					part_count = result['part_count']
				if 'part' in result and 'code' in result['part']:
					match = re.search('src="([^"]+)', result['part']['code'])
					if match:
						url = match.group(1)
						return url
		return False
