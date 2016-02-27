import sys
import os
import re
import urllib
from urlparse import urlparse
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult
class ororoScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='ororo'
		self.name = 'ororo.tv'
		self.referrer = 'http://ororo.tv'
		self.base_url = 'http://ororo.tv'
		self.username = ADDON.get_setting(self.service + '_username')
		self.password = ADDON.get_setting(self.service + '_password')
		self.include_paid = ADDON.get_setting(self.service + '_premium') == "true"
		self.require_auth = True

	def check_authentication(self, username, password):
		valid = False
		return True
		return valid
	
	def request2(self):
		uri = '/nl'
		tries = 0
		while True:
			html = self.request(uri)
			if html.startswith('http://') and tries < 10:
				tries += 1
				url = html
			else:
				break
		if re.search('You are already signed in', html):
			return html
		uri = '/en/users/sign_in'
		data = {'user[email]': self.username, 'user[password]': self.password, 'user[remember_me]': 1}
		html = self.request(uri, data)
		#if '<li><a href="/en/users/sign_out">Log out</a></li>' in html:
		if '<meta name="csrf-param" content="authenticity_token" />' in html:
			return html
		else:
			ADDON.log('Login Failed.')

			return False
		
		
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'], args['year'])
		if uri:
			html = self.request(uri, headers={'X-Requested-With': 'XMLHttpRequest'})
			results = self.process_results(html)
			
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		if uri:
			html = self.request(uri, headers={'X-Requested-With': 'XMLHttpRequest'})
			results = self.process_results(html)
		return results
	

	def get_resolved_url(self, raw_url):
		return raw_url

	
	def process_results(self, html):		
		results = []

		pattern = "source src='([^']+)'\s+type='video/([^']+)"
		for match in re.finditer(pattern, html):
			url = match.group(1)
			url = url.replace('&amp;', '&')
			temp = urlparse(url)
			title = temp.path.split('/')[-1]
			url += '|User-Agent=%s' % (self.get_user_agent())
			url = "%s://%s" % (self.service, url)
			host_name = 'ororo.tv'
			extension = match.group(2)
			result = ScraperResult(self.service, host_name, url, title)
			result.quality = QUALITY.HD720
			result.extension = extension
			results.append(result)
		return results
		
	def prepair_query(self, media, *args, **kwards):
		html = self.request2()
		if media == 'tvshow':
			if html:
				import HTMLParser
				h = HTMLParser.HTMLParser()
				for match in re.finditer('<span class=\'value\'>(\d{4})(.*?)href="([^"]+)[^>]+>([^<]+)', html, re.DOTALL):
					match_year, middle, uri, match_title = match.groups()
					if not self.include_paid and 'paid accounts' in middle:
						continue
					if h.unescape(match_title) == args[0] and int(args[3]) == int(match_year):
						html = self.request(uri)
						pattern = 'data-href="([^"]+)[^>]*class="episode"\s+href="#%s-%s"' % (args[1], args[2])
						match = re.search(pattern, html, re.DOTALL)
						if match:
							uri = match.group(1)
							return uri
		else:
			html = self.request('/en/movies')
			if html:
				import HTMLParser
				h = HTMLParser.HTMLParser()
				for match in re.finditer('<span class=\'value\'>(\d{4})(.*?)href="([^"]+)[^>]+>([^<]+)', html, re.DOTALL):
					match_year, middle, uri, match_title = match.groups()
					if not self.include_paid and 'paid accounts' in middle:
						continue
					if h.unescape(match_title) == args[0] and int(args[1]) == int(match_year):
						uri += '/video'
						return uri
		return False