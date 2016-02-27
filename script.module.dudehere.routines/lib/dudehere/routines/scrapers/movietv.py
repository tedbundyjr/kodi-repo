import sys
import os
import re
import time
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult

class movietvScraper(CommonScraper):
	token = None
	def __init__(self):
		self.service='movietv'
		self.name = 'movietv.to'
		self.referrer = 'http://www.movietv.to'
		self.base_url = 'http://www.movietv.to'
		self.timeout = 2

		
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'], args['year'])
		if uri:
			uri += '&_=%s' % (str(int(time.time()) * 1000))
			uri += '&token=%s' % (self.get_token())
			js = self.request(uri, headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': self.referer}, return_json=True)
			results = self.process_tv_results(js)
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		if uri:
			uri += '&_=%s' % (str(int(time.time()) * 1000))
			uri += '&token=%s' % (self.get_token())
			js = self.request(uri, headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': self.referer})
			results = self.process_movie_results(js)
		return results
	
	def process_tv_results(self, js):
		results = []
		url = "%s://%s" % (self.service, js['url'])
		result = ScraperResult(self.service, 'movietv', url)
		result.quality = QUALITY.HD720
		results.append(result)
		return results
	
	def process_movie_results(self, html):
		results = []
		for match in re.finditer('var\s+(videolink[^\s]*)\s*=\s*"([^"]+)', html):
			var_name, url = match.groups()
			url = "%s://%s" % (self.service, url)
			result = ScraperResult(self.service, 'movietv', url)
			if 'hd' in var_name:
				result.quality = QUALITY.HD1080
			else:
				result.quality = QUALITY.HD720
			results.append(result)
		return results
	
	def get_resolved_url(self, raw_url):
		resolved_url = raw_url
		return resolved_url
		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			uri = '/index/loadmovies'
			self.referer = self.base_url + '/series'
			data = {'loadmovies': 'showData', 'page': 1, 'abc': 'All', 'genres': '', 'sortby': 'Popularity', 'quality': 'All', 'type': "tv", 'q': args[0], 'token': self.get_token()}
			soup = self.request(uri, data, headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': self.referer}, return_soup=True)
			for div in soup.findAll('div', {"class": "item"}):
				match = re.search('href="([^"]+).*?class="movie-title">\s*([^<]+).*?movie-date">(\d+)', str(div), re.DOTALL)
				if match:
					uri, title, year = match.groups() 
					if title == args[0] and year == str(args[3]):
						self.referer = self.base_url + uri
						uri += '&_=%s' % (str(int(time.time()) * 1000))
						uri += '&token=%s' % (self.get_token())
						html = self.request(uri)
						match = re.search("var\s+id\s*=\s*'?(\d+)'?", html)
						if match:
							show_id = match.group(1)
							uri = '/series/season?id=%s&s=%s&_=%s&token=%s' % (show_id, args[1], str(int(time.time()) * 1000), self.get_token())
							data = self.request(uri, headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': self.referer}, return_json=True)
							for episode in data:
								if int(episode['episode_number']) == int(args[2]):
									return '/series/getLink?id=%s&s=%s&e=%s' % (show_id, args[1], args[2])
			
		else:
			uri = '/index/loadmovies'
			self.referer = self.base_url
			data = {'loadmovies': 'showData', 'page': 1, 'abc': 'All', 'genres': '', 'sortby': 'Popularity', 'quality': 'All', 'type': "movie", 'q': args[0], 'token': self.get_token()}
			soup = self.request(uri, data, headers = {'X-Requested-With': 'XMLHttpRequest', 'Referer': self.referer}, return_soup=True)
			for div in soup.findAll('div', {"class": "item"}):
				match = re.search('href="([^"]+).*?class="movie-title">\s*([^<]+).*?movie-date">(\d+)', str(div), re.DOTALL)
				if match:
					uri, title, year = match.groups() 
					if title == args[0] and year == str(args[1]):
						self.referer = self.base_url + uri
						return uri
		return False
	
	def get_token(self):
		if self.token is None:
			headers = {'Referer': self.referrer}
			html =self.request('/', headers=headers)
			match = re.search('var\s+token_key\s*=\s*"([^"]+)', html)
			if match:
				self.token = match.group(1)

		return self.token
	
