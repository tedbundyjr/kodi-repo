'''
watchepisode.tv source plugin
@natko1412, 2015

'''

import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult



class watchepisodeScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='watchepisode'
		self.name = 'watchepisode'
		self.referrer = 'http://www.watchepisode.tv'
		self.base_url = 'http://www.watchepisode.tv'

	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'],args['year'])
		soup = self.request(uri, return_soup=True)
		if soup:
			results = self.process_results(soup)
		return results
	
	
	def search_movie(self, args):
		return []

	def process_results(self, soup):
		results = []
		rows=soup.findAll('div',{'class':'site'})
		for i in range(0,len(rows)):
			try:
				row=rows[i]
				domain=row.find('a')['data-hostname'].lower()
				link=row.find('a')['data-actuallink']
				host_name = domain
				if self.filter_host(host_name):
					url = "%s://%s" % (self.service, link)
					result = ScraperResult(self.service, host_name, url)
					result.quality = QUALITY.UNKNOWN
					results.append(result)	
			except:
				pass
		return results
		
		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			showname = args[0]
			showname=re.sub(r'[^\w\s]','',showname).lower().replace(" ", "-")

			season = str(args[1]).lstrip('0')
			episode = str(args[2]).lstrip('0')

			urll='/%s'%(showname)
			soup=self.request(urll, return_soup=True)
			items=soup.findAll('div',{'class':'el-item '})
			for item in items:
				title= item.find('a')['title']
				if 'Season %s Episode %s'%(season,episode) in title:
					url=item.find('a')['href']
					return url.replace(self.base_url,'')
					break