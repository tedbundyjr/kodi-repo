#!/usr/bin/python
# -*- coding: utf-8 -*-
PYTHONIOENCODING="UTF-8"
import sys
import os
import re
import urllib
from dudehere.routines import *
from dudehere.routines.vfs import VFSClass
from dudehere.routines.scrapers import CommonScraper, ScraperResult



class releasebbScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='releasebb'
		self.name = 'releasebb'
		self.referrer = 'http://rlsbb.com'
		self.base_url = 'http://rlsbb.com'
		self.timeout = 5
		self.table = {
			"rapidgator": "rapidgator.net",
			"uploaded": "uploaded.net",
			"alfafile": "alfafile.net",
			"vip file": "vipfile.in",
			"netload": "netload.in",
			"turbobit": "turbobit.net"
		}
	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('tvshow', args['showname'], args['season'], args['episode'],args['year'])
		if uri:
			soup = self.request(uri, timeout=5, return_soup=True)
			results = self.process_results(soup)
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = self.prepair_query('movie', args['title'], args['year'])
		if uri:
			soup = self.request(uri, timeout=10, return_soup=True)
			if soup:
				results = self.process_movie_results(soup)
		return results
	
	def process_results(self, soup):
		vfs = VFSClass()
		results = []

		blocks = soup.findAll('div', {"class": "postContent"})
		for block in blocks:
			links = block.findAll('p', {"style": "text-align: center;"})
			for link in links:
				files = link.findAll('a')
				size = re.search('\s(\d+\.??\d+)(MB|GB)', str(link))
				if size:
					if size.group(2) == 'MB':
						size = int(size.group(1)) * 1000 * 1000
					else:
						size = float(size.group(1)) * 1000 * 1000 * 1000

				for file in files:
					if file.text.lower() not in self.table: continue
					url = file['href']
					quality = self.test_quality(url, default=QUALITY.HIGH)
					host_name = self.table[file.text.lower()]
					path = vfs.path_parts(url)
					url = "%s://%s" % (self.service, url)
					try: 
						filename =  path['path'].split('/')[-1]
					except:
						filename = self.service
					result = ScraperResult(self.service, host_name, url, filename)
					result.quality = quality
					if size: result.size = size
					if path['extension'] != 'html':
						result.extension = path['extension']
					results.append(result)
		return results
	

	def process_movie_results(self, soup):
		results = []
		
		block = soup.find('div', {"class": "postContent"})
		block_string = str(block)
		filename = re.search('Release Name:</strong> (.+?)<br />', block_string)
		if filename:
			filename = filename.group(1)
		else:
			filename = self.service
		size = re.search('\s(\d+\.??\d+)\s??(MB|GB)', block_string)	
		if size:
			if size.group(2) == 'MB':
				size = int(size.group(1)) * 1000 * 1000
			else:
				size = float(size.group(1)) * 1000 * 1000 * 1000

		blocks = block.findAll('p')
		for block in blocks:
			test = block.findChildren()
			if test[0].text == 'Download:':
				break
		files = block.findAll('a')
		for file in files:
			url = file['href']
			if file.text.lower() not in self.table or 'nfo.rlsbb.com' in url: continue
			
			quality = self.test_quality(url, default=QUALITY.HIGH)
			url = "%s://%s" % (self.service, url)
			host_name = self.table[file.text.lower()]
			result = ScraperResult(self.service, host_name, url, filename)
			result.quality = quality
			if size:
				result.size = size
				
			results.append(result)
		return results

		
	def prepair_query(self, media, *args, **kwards):
		if media == 'tvshow':
			uri = '/%s-s%se%s' % (args[0].replace(' ', '-'), str(args[1]).zfill(2), str(args[2]).zfill(2))
		else:
			uri = '/%s-%s' % (args[0].replace(' ', '-'), args[1])
		return uri
	
