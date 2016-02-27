'''
projectfreetv.so source plugin
@natko1412, 2015
'''

import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult



class projectfreetvScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='projectfreetv'
		self.name = 'projectfreetv'
		self.referrer = 'http://projectfreetv.so'
		self.base_url = 'http://projectfreetv.so'

	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'],args['year'])
		soup = self.request(uri, return_soup=True)
		if soup:
			results = self.process_results(soup)
		return results
	
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		soup = self.request(uri, return_soup=True)
		results = self.process_results(soup)
		return results

	def process_results(self, soup):
		results = []
		rows=soup.findAll('tr')
		for i in range(0,len(rows)):
			try:
				row=rows[i]
				link=row.find('td').find('a')['href']
				import HTMLParser
				h = HTMLParser.HTMLParser()
				dm=row.find('td').getText()
				domain=h.unescape(dm).strip()
				try:
					quality=row.findAll('td')[3].find('img')['src']
				except:
					quality=''
				host_name = domain
				if self.filter_host(host_name):
					url = "%s://%s" % (self.service, link)
					result = ScraperResult(self.service, host_name, url)
					if 'qualityDVD' in quality:
						result.quality = QUALITY.SD480
					elif 'qualityhd' in quality:
						result.quality = QUALITY.SD720
					else:
						result.quality = QUALITY.UNKNOWN

					results.append(result)	
			except:
				pass
		return results
	def get_hostname(self,link):
		reg=re.compile("http://(.+?)/")
		domain=re.findall(reg,link)[0]
		domain=domain.replace('www.','').replace('embed.','').replace('beta.','')
		return domain

	def get_resolved_url(self, raw_url):
		url=raw_url.replace(self.base_url,'')
		soup = self.request(url, return_soup=True)
		#raw_link=soup.find('div',{'style':'float:left;width:300px;height:150px;'}).find('a')['href']
		div = soup.find('div',{'style':'float:left;width:300px;height:150px;'})
		if div:
			a = div.find('a')
			if a:
				raw_url = a['href']
				return self.do_urlresolver(raw_url)
		return None
	
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			showname = args[0].lower().replace(" ", "-")
			season = str(args[1])
			episode = str(args[2])

			url='/%s-season-%s-episode-%s/'%(showname,season,episode)
			return url
		elif media=='movie':
			title=args[0].replace(' ','-')
			year=args[1]
			url='/movies/%s-%s/'%(title,year)
			return url