import sys
import os
import re
import urllib
import random
import urlparse
from BeautifulSoup import BeautifulSoup
from dudehere.routines import *
from dudehere.routines.scrapers import CommonScraper, ScraperResult

class icefilmsScraper(CommonScraper):
	def __init__(self):
		self._settings = {}
		self.service='icefilms'
		self.name = 'icefilms.info'
		self.base_url = 'http://www.icefilms.info'
		self.referrer = 'http://www.icefilms.info'
		self.referer  = '/membersonly/components/com_iceplayer/video.php?h=374&w=631&vid=%s&img='
		self.ajax_url = '/membersonly/components/com_iceplayer/video.phpAjaxResp.php?id=%s&s=%s&iqs=&url=&m=%s&cap=+&sec=%s&t=%s&ad_url=%s'
	
	
	def search_tvshow(self, args):
		self.domains = args['domains']
		results = []
		uri = "/tv/a-z/%s" % re.sub('^(A )|(An )|(The )', '', args['showname'], re.IGNORECASE)[0:1]
		html = self.request(uri)
		pattern = "<a href=/tv/series/(\d+?)/(\d+?)>%s \(%s\)</a>" % (args['showname'], args['year'])
		show = re.search(pattern, html)
		if show:
			pattern = '%sx%s' % (args['season'], str(args['episode']).zfill(2))
			uri = "/tv/series/%s/%s" % (show.group(1), show.group(2))
			soup = self.request(uri, return_soup=True)
			for star in soup.findAll("img", {"class": "star"}):
				a = star.nextSibling
				if re.search(pattern, a.string):
					uri = a['href']
					vid = re.search('=(\d+?)&', uri).group(1)
					return self._get_sources(vid)
					break
		return results
	
	def search_movie(self, args):
		self.domains = args['domains']
		results = []
		uri = "/movies/a-z/%s" % re.sub('^(A )|(An )|(The )', '', args['title'], re.IGNORECASE)[0:1]
		html = self.request(uri)
		pattern = "<a href=/ip.php\?v=(\d+?)&>%s \(%s\)</a>" % (args['title'], args['year'])
		movie = re.search(pattern, html)
		if movie:
			return self._get_sources(movie.group(1))
		return results
	
	def get_resolved_url(self, raw_url):
		uri, query = raw_url.split('?', 1)
		data = urlparse.parse_qs(query, True)
		uri += '?s=%s&t=%s&app_id=DHCR' % (data['id'][0], data['t'][0])
		referer = self.referer % (data['t'][0])
		try:
			ad_url = urllib.unquote(data['ad_url'][0])
			del data['ad_url']
		except:
			pass
		headers = {"Referer": referer}
		params = {}
		for key in data.keys():
			params[key] = data[key][0]
		html = self.request(uri, params, headers=headers)
		match = re.search('url=(.*)', html)
		if match:
			raw_url = urllib.unquote_plus(match.group(1))
			return self.do_urlresolver(raw_url)
		return ''
	
	def _get_sources(self, vid):
		uri = self.referer % vid
		results = []
		html = self.request(uri)
		soup = BeautifulSoup(html)
		
		match = re.search('lastChild\.value="([^"]+)"(?:\s*\+\s*"([^"]+))?', html)
		secret = ''.join(match.groups(''))

		match = re.search('"&t=([^"]+)', html)
		t = match.group(1)

		match = re.search('(?:\s+|,)s\s*=(\d+)', html)
		s_start = int(match.group(1))

		match = re.search('(?:\s+|,)m\s*=(\d+)', html)
		m_start = int(match.group(1))
		
		match = re.search('<iframe[^>]*src="([^"]+)', html)
		if match:
			ad_url = urllib.quote(match.group(1))
		else:
			ad_url = ''
			
		for block in soup.findAll('div', {"class": "ripdiv"}):
			isHD = 'HD 720p' in block.find('b').string
			if isHD: quality = QUALITY.HD720
			else: quality = QUALITY.SD480
			
			mirrors = block.findAll("p")
			for mirror in mirrors:
				links = mirror.findAll("a")
				for link in links:
					mirror_id = link['onclick'][3:len(link['onclick'])-1]
					host_name, title = self.get_provider(link)
					if host_name:
						if self.filter_host(host_name):
							s = s_start + random.randint(3, 1000)
							m = m_start + random.randint(21, 1000)
							uri = self.ajax_url % (mirror_id, s, m, secret, t, ad_url)
							url = "%s://%s" % (self.service, uri)
							result = ScraperResult(self.service, host_name, url, title)
							result.quality = quality
							results.append(result)
		return results
		
	def get_provider(self, link):
		title = link.next[0:len(link.next)-2]
		s = re.search('Source #(\d+): (.+?)</a>', str(link))
		skey = self.strip_tags(s.group(2)).lower()
		table = {
				'180upload': 		'180upload.com',
				'hugefiles':		'hugefiles.net',
				'clicknupload':		'clicknupload.com',
				'tusfiles':			'tusfiles.net',
				'xfileload':		'xfileload.com',
				'mightyupload':		'mightyupload.com',
				'movreel':			'movreel.com',
				'donevideo':		'donevideo.com',
				'vidplay':			'vidplay.net',
				'24uploading':		'24uploading.com',
				'xvidstage':		'xvidstage.com',
				'2shared':			'2shared.com',
				'upload':			'upload.af',
				'uploadx':			'uploadx.org',
		}
		if skey in table.keys():
			return table[skey], title
		else: 
			ADDON.log("Icefilms unmatched host: %s" % skey)
		return None, None

	def strip_tags(self, html):
		import htmlentitydefs
		from HTMLParser import HTMLParser
		class HTMLTextExtractor(HTMLParser):
			def __init__(self):
				HTMLParser.__init__(self)
				self.result = [ ]
		
			def handle_data(self, d):
				self.result.append(d)
		
			def handle_charref(self, number):
				codepoint = int(number[1:], 16) if number[0] in (u'x', u'X') else int(number)
				self.result.append(unichr(codepoint))
		
			def handle_entityref(self, name):
				codepoint = htmlentitydefs.name2codepoint[name]
				self.result.append(unichr(codepoint))
				
			def get_text(self):
				return u''.join(self.result)	
				
		s = HTMLTextExtractor()
		s.feed(html)
		return s.get_text()
		