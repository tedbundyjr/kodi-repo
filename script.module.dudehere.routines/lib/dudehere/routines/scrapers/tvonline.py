'''
tvonline.tw source plugin
@natko1412, 2015

'''

import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult



class tvonlineScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='tvonline'
		self.name = 'tvonline'
		self.referrer = 'http://tvonline.tw'
		self.base_url = 'http://tvonline.tw'

	
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
		tag=str(soup.find('div',{'id':'linkname'}))
		reg=re.compile("go_to\(\d+,'(.+?)'\)")
		links=list(re.findall(reg,tag))
		for link in links:
			host_name = self.get_hostname(link)
			if self.filter_host(host_name):
				url = "%s://%s" % (self.service, link)
				result = ScraperResult(self.service, host_name, url)
				result.quality = QUALITY.UNKNOWN
				results.append(result)	
		return results
	def get_hostname(self,link):
		reg=re.compile("http://(.+?)/")
		domain=re.findall(reg,link)[0]
		domain=domain.replace('www.','').replace('embed.','').replace('beta.','')
		return domain

		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			showname = args[0]#.lower().replace(" ", "_")
			season = str(args[1])
			episode = str(args[2])
			try:
				year=int(args[3])
			except:
				year=0
			
			url='/search.php?key=%s'%(urllib.quote_plus(showname))
			soup=self.request(url, return_soup=True)
			shows=soup.findAll('a',{'target':'_blank'})
			for show in shows:
				link=show['href']
				show_title=show.getText()
				
				try:	show_year=int(re.compile('\((\d+)\)').findall(show_title)[0])
				except: show_year=''
				if show_year==year:
					return '/'+ link+'season-%s-episode-%s'%(season.lstrip("0"),episode.lstrip("0"))+'/'
			