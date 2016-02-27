import sys
import os
import re
import urllib
import urllib2
import json
import time
import socket
import unicodedata
import xbmcgui
import xbmcaddon
import urlresolver
import hashlib
import random
from urlparse import urljoin
from dudehere.routines import *
from dudehere.routines.threadpool import ThreadPool
from addon.common.net import Net, HttpResponse
from BeautifulSoup import BeautifulSoup
from dudehere.routines.vfs import VFSClass
from dudehere.routines import cloudflare
from dudehere.routines.plugin import ProgressBar
vfs = VFSClass()
DECAY = 2
SCRAPER_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_PATH = vfs.join(DATA_PATH,'cookies')
if not vfs.exists(COOKIE_PATH): vfs.mkdir(COOKIE_PATH, recursive=True)
sys.path.append(SCRAPER_DIR)
RD_HOSTS = []
if ADDON.get_setting('database_type')=='1':
	DB_NAME = ADDON.get_setting('database_mysql_name')
	DB_USER = ADDON.get_setting('database_mysql_user')
	DB_PASS = ADDON.get_setting('database_mysql_pass')
	DB_PORT = ADDON.get_setting('database_mysql_port')
	DB_ADDRESS = ADDON.get_setting('database_mysql_host')
	DB_TYPE = 'mysql'
	from dudehere.routines.database import MySQLDatabase as DatabaseAPI

else:
	DB_TYPE = 'sqlite'
	DB_FILE = xbmc.translatePath(ADDON.get_setting('database_sqlite_file'))
	from dudehere.routines.database import SQLiteDatabase as DatabaseAPI

class MyDatabaseAPI(DatabaseAPI):
	def _initialize(self):
		root = xbmcaddon.Addon('script.module.dudehere.routines').getAddonInfo('path')
		schema_file = vfs.join(root, 'resources/database/schema.%s.sql' % self.db_type)
		if self.run_script(schema_file, commit=False):
			self.execute('DELETE FROM version WHERE 1')
			self.execute('INSERT INTO version(db_version) VALUES(?)', [self.db_version])
			self.commit()
	
	def do_init(self):
		do_init = True
		try:
			test = self.query("SELECT 1 FROM version WHERE db_version >= ?", [self.db_version])
			if test:
				do_init = False
		except:
			do_init = True
		return do_init


DB_VERSION = 6
if DB_TYPE == 'mysql':
	DB=MyDatabaseAPI(DB_ADDRESS, DB_NAME, DB_USER, DB_PASS, DB_PORT, version=DB_VERSION, connect=False)
else:
	DB = MyDatabaseAPI(DB_FILE, version=DB_VERSION, connect=False)

class NoRedirection(urllib2.HTTPErrorProcessor):
	def http_response(self, request, response):
		return response
	https_response = http_response

class NetLib(Net):
	timeout=1
	get_redirect = False
	def get(self, url, headers=None, timeout=1):
		self.timeout = timeout
		html = self.http_GET(url, headers=headers)
		return html
	
	def post(self, url, params, headers=None, timeout=1):
		self.timeout = timeout
		html = self.http_POST(url, params, headers=headers)
		return html
		
	def _fetch(self, url, form_data={}, headers={}, compression=True):
		encoding = ''
		req = urllib2.Request(url)
		if form_data:
			form_data = urllib.urlencode(form_data)
			req = urllib2.Request(url, form_data)
		req.add_header('User-Agent', self._user_agent)
		for k, v in headers.items():
			req.add_header(k, v)
		if compression:
			req.add_header('Accept-Encoding', 'gzip')
		try:
			if self.get_redirect:
				opener = urllib2.build_opener(NoRedirection)
				urllib2.install_opener(opener)
				response = urllib2.urlopen(req, timeout=self.timeout)
				if response.info().getheader('Refresh') is not None:
					refresh = response.info().getheader('Refresh')
					return refresh.split(';')[-1].split('url=')[-1]
				else:
					return response.info().getheader('Location')
			else:
				response = urllib2.urlopen(req, timeout=self.timeout)


				
		except urllib2.HTTPError as e:
			if e.code == 503 and 'cf-browser-verification' in e.read():
				html = cloudflare.solve(url, self._cjf, self._user_agent)
				return html
			else:
				ADDON.log("Scraper-HTTP Error: %s" % e.code)
				ADDON.log(url)
				return ''
		except urllib2.URLError as e:
			ADDON.log("Scraper-URL Error: %s" % e)
			ADDON.log(url)
			return ''
		except socket.timeout as e:
			ADDON.log("Scraper-Timeout Error: %s" % e)
			ADDON.log(url)
			return ''
		
		return HttpResponse(response).content

class ScraperResult():
	bitrate_color = ADDON.get_setting('custom_color_bitrate') if ADDON.get_setting('custom_color_bitrate') != '' else 'purple'
	hostname_color = ADDON.get_setting('custom_color_hostname') if ADDON.get_setting('custom_color_hostname') != '' else 'red'
	size_color = ADDON.get_setting('custom_color_filesize') if ADDON.get_setting('custom_color_filesize') != '' else 'blue'
	extension_color = ADDON.get_setting('custom_color_extension') if ADDON.get_setting('custom_color_extension') != '' else 'green'
	quality_color = ADDON.get_setting('custom_color_quality') if ADDON.get_setting('custom_color_quality') != '' else 'yellow'
	service_color = ADDON.get_setting('custom_color_service') if ADDON.get_setting('custom_color_service') != '' else 'white'
	debrid_color = ADDON.get_setting('custom_color_debrid_color') if ADDON.get_setting('custom_color_debrid_color') != '' else 'hotpink'
	host_cleaner = re.compile('[^a-z0-9\.]', re.IGNORECASE)
	
	def __init__(self, service, hostname, url, text=None):
		hostname = self.host_cleaner.sub('', hostname)
		if hostname.startswith('www.'):
			hostname = hostname.replace('www.', '')
		self.hostname = hostname
		self.service = service
		if text is not None:
			self.text = text.strip(' \t\n\r')
		else:
			self.text = text
		self.url = url
		self.bitrate = None
		self.size = None
		self.extension = None
		self.quality = None
		self.score = 0
		self.PB = False
		self.debrid = 0
		self.alldebrid = 0
		self.realdebrid = 0
		self.rpnet = 0
		self.premiumize = 0
	
	def colorize(self, attrib, value):
		color = getattr(self, attrib+'_color')
		if attrib == 'bitrate':
			return "[COLOR %s]%s kb/s[/COLOR]" % (color, value)
		elif attrib == 'quality':
			quality = QUALITY.r_map[value]
			return "[COLOR %s]%s[/COLOR]" % (color, quality)
		elif attrib == 'size':
			size = self.format_size(value)
			return "[COLOR %s]%s[/COLOR]" % (color, size)
		else:
			return "[COLOR %s]%s[/COLOR]" % (color, value)
	
	def format_size(self, size):
		size = int(size) / (1000 * 1000)
		if size > 2000:
			size = size / 1000
			unit = 'GB'
		else :
			unit = 'MB'
		size = "%s %s" % (size, unit)
		return size
		
	def ck(self, attrib):
		if getattr(self, attrib):
			self.attributes.append(self.colorize(attrib, getattr(self, attrib)))
		
	def format(self):
		debrid_hosts = ADDON.load_data(vfs.join(DATA_PATH, 'debrid_hosts.cache'))
		
		self.attributes = []
		self.attributes.append(self.colorize('hostname', self.hostname))
		self.attributes.append(self.colorize('service', self.service))
		debrid = []
		#print debrid_hosts
		if 'ad' in debrid_hosts:
			if self.hostname in debrid_hosts['ad']:
				self=alldebrid = 1
				debrid.append('AD')

		if 'rp' in debrid_hosts:
			if self.hostname in debrid_hosts['rp']:
				self.rpnet = 1
				debrid.append('RPN')

		if 'rd' in debrid_hosts:
			if self.hostname in debrid_hosts['rd']:
				self.realdebrid = 1
				debrid.append('RD')

		if 'pm' in debrid_hosts:
			if self.hostname in debrid_hosts['pm']:
				self.premiumize = 1
				debrid.append('PM')

			
		if len(debrid):
			self.attributes.append(self.colorize('debrid', ','.join(debrid)))
			self.debrid = 1
			
		for foo in ['size', 'bitrate', 'extension', 'quality']:
			self.ck(foo)
		
		format = "[%s]: %s"	
		if self.text is None: self.text = self.hostname
		try:
			format = format % (' | '.join(self.attributes), self.text)
		except UnicodeEncodeError:
			for k in attributes:
				if isinstance(attributes[k], unicode):
					attributes[k] = attributes[k].encode('utf-8')
			format = format % (' | '.join(self.attributes), self.text)
		return format

class CommonScraper():
	USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
	ACCEPT = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
	accept = ACCEPT
	user_agent = USER_AGENT
	HOST_COLOR = 'red'
	SIZE_COLOR = 'blue'
	EXTENSION_COLOR = 'green'
	QUALITY_COLOR = 'yellow'
	BITRATE_COLOR = 'purple'
	timeout = 1
	broken = False
	require_auth = False
	is_cachable = True
	show_scraper_progress = ADDON.get_setting('enable_scraper_progress') == 'true'
	PB = False
	host_cleaner = re.compile('[^a-z0-9\.]', re.IGNORECASE)
	
	def __init__(self, load = None, disable = None, cache_results=False):
		self.threadpool_size = 5
		self.cache_results = cache_results
		self._load_list = load
		self._disable_list = disable
		self.enabled_scrapers = 0
		self.active_scrapers = []
		self.supported_scrapers = []
		self._active_scrapers = []
		self._load_scrapers()
		self._enable_scrapers()
		self.search_results = []
		self.show_scraper_progress = ADDON.get_setting('enable_scraper_progress') == 'true'
		
		expired = True
		self.filters = False
		if ADDON.get_setting('enable_result_filters') == 'true':
			cache_file = vfs.join(DATA_PATH, 'filters.cache')
			if vfs.exists(cache_file):
				self.filters = ADDON.load_data(cache_file)
		cache_file = vfs.join(DATA_PATH, 'debrid_hosts.cache')
		if vfs.exists(cache_file):
			timestamp = int(time.time())
			m_time = vfs.get_stat(cache_file).st_mtime()
			if (timestamp - m_time) < 86400: expired = False
		
		if expired:
			hosts = {"pm": [], "rd": [], "ad": [], "rp": []}
			net = Net()
			try:
				customer_id = xbmcaddon.Addon('script.module.urlresolver').getSetting('PremiumizeMeResolver_username')
				pin = xbmcaddon.Addon('script.module.urlresolver').getSetting('PremiumizeMeResolver_password')
				query = {"method": "hosterlist", "params[login]": customer_id, "params[pass]": pin}
				api_url = "http://api.premiumize.me/pm-api/v1.php?" + urllib.urlencode(query)
				response = net.http_GET(api_url).content
				data = json.loads(response)
				if 'result' in data:
					hosts['pm'] = data['result']['hosterlist']
			except: pass

			try:
				response = Net().http_GET('http://real-debrid.com/api/hosters.php').content
				hosts['rd'] = [x.strip('"') for x in response.split(',')]
			except: pass
			
			try:
				response = Net().http_GET('http://alldebrid.com/api.php?action=get_host').content
				hosts['ad'] = [x.strip('"') for x in response.split(',\n')]
			except: pass
				
			try:
				response = Net().http_GET('http://premium.rpnet.biz/hoster2.json').content
				hosts['rp'] = json.loads(response)['supported']
			except: pass

			ADDON.save_data(cache_file, hosts)
	
	def get_user_agent(self):
		user_agent = ADDON.get_setting('user_agent')
		try: agent_refresh_time = int(ADDON.get_setting('agent_refresh_time'))
		except: agent_refresh_time = 0
		if not user_agent or agent_refresh_time < (time.time() - (7 * 24 * 60 * 60)):
			user_agent = self.generate_user_agent()
			ADDON.set_setting('user_agent', user_agent)
			ADDON.set_setting('agent_refresh_time', str(int(time.time())))
		return user_agent

	def generate_user_agent(self):
		BR_VERS = [
			['%s.0' % i for i in xrange(18, 43)],
			['41.0.2228.0', '41.0.2227.1', '41.0.2227.0', '41.0.2226.0', '40.0.2214.93', '37.0.2062.124'],
			['11.0'],
			['11.0']
		]
		WIN_VERS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0', 'Windows NT 5.1', 'Windows NT 5.0']
		FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
		RAND_UAS = [
			'Mozilla/5.0 ({win_ver}{feature}; rv:{br_ver}) Gecko/20100101 Firefox/{br_ver}',
			'Mozilla/5.0 ({win_ver}{feature}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{br_ver} Safari/537.36',
			'Mozilla/5.0 ({win_ver}{feature}; Trident/7.0; rv:{br_ver}) like Gecko'
		]
		index = random.randrange(len(RAND_UAS))
		user_agent = RAND_UAS[index].format(win_ver=random.choice(WIN_VERS), feature=random.choice(FEATURES), br_ver=random.choice(BR_VERS[index]))
		
		return user_agent

	def clean_hostname(self, hostname):
		return self.host_cleaner.sub('', hostname)
	
	def filter_host(self, host_name):
		if self.domains is None:
			return True
		if host_name in self.domains:
			return True
		return False

	def reinitialize_cache(self):
		vfs.rm(DB_FILE)
		DB=MyDatabaseAPI(DB_FILE, init_flag='database_sqlite_init.cache')
		DB._initialize()
	
	def normalize(self, string):
		return unicodedata.normalize('NFKD', unicode(string)).encode('utf-8','ignore')
	
	def get_setting(self, k):
		return self._settings[k]
	
	def set_setting(self, k, v):
		self._settings[k] = v
	
	def get_property(self, k):
		p = xbmcgui.Window(10000).getProperty('GenericPlaybackService.' + k)
		if p == 'false': return False
		if p == 'true': return True
		return p
	
	def set_property(self, k, v):
		xbmcgui.Window(10000).setProperty('GenericPlaybackService.' + k, v)
	
	def clear_property(self, k):
		xbmcgui.Window(10000).clearProperty('GenericPlaybackService.' + k)
	
	def get_host_list(self):
		DB.connect()
		hosts = DB.query_assoc("SELECT host, weight, disabled FROM host_weights ORDER BY weight, host ASC", force_double_array=True)
		DB.disconnect()
		return hosts
	
	def toggle_host(self, host):
		DB.connect()
		DB.execute("UPDATE host_weights SET disabled = (disabled * -1 + 1) WHERE host=?",  [host])
		DB.commit()
		DB.disconnect()
	
	def change_host_weight(self, host, weight):
		DB.connect()
		DB.execute("UPDATE host_weights SET weight=? WHERE host=?",  [weight, host])
		DB.commit()
		DB.disconnect()
	
	def read_scraper_states(self):
		DB.connect()
		results = DB.query_assoc("SELECT name, enabled FROM scraper_states ORDER BY name ASC")
		DB.disconnect()
		return results
	
	def toggle_scraper_state(self, name):
		DB.connect()
		DB.execute("UPDATE scraper_states SET enabled = (enabled * -1 + 1) WHERE name=?",  [name])
		DB.commit()
		DB.disconnect()
		
	def set_scraper_state(self, name, state):
		DB.connect()
		state = 1 if state else 0
		DB.execute("UPDATE scraper_states SET enabled = ? WHERE name=?",  [state, name])
		DB.commit()
		DB.disconnect()
		
	def _load_scrapers(self):
		DB.connect()
		names = []
		count = 0
		for filename in sorted(os.listdir(SCRAPER_DIR)):
			if not re.search('(__)|(common\.py)|(example\.py)|(all\.py)', filename) and re.search('py$', filename):
				name = filename[0:len(filename)-3]
				self.supported_scrapers.append(name)
				names.append([name])
				if self._load_list is False: continue 	#should I even load anything?
				skip = False
				
				if self._load_list == 'all':
					pass 					#load all except explicitly disabled
				elif isinstance(self._load_list, list):
					skip = True				#load all in the supplied load list except explicitly disabled
					if name in self._load_list: skip = False
				else:
					skip = True				#load all enabled from db except explicitly disabled
					if DB.query("SELECT 1 FROM scraper_states WHERE enabled AND name=?", [name]): skip = False
						
				if self._disable_list is not None:
					if name in self._disable_list:
						skip = True			#now disable any scrapers in the disable list
				if skip is False:	
					classname = name+'Scraper'
					scraper = __import__(name, globals(), locals(), [classname], -1)
					klass = getattr(scraper, classname)
					scraper = klass()
					self.put_scraper(scraper.service, scraper)
				count +=1
		if count > DB.query("SELECT count(1) FROM scraper_states")[0]:
			for name in names: DB.execute("INSERT INTO scraper_states(name) VALUES (?)", name)
			DB.commit()
		DB.disconnect()
				
	def get_scraper_by_name(self, name):
		try:
			index = self.active_scrapers.index(name)
			return self.get_scraper_by_index(index)
		except:
			return None
		
	def get_scraper_by_index(self, index):
		try:
			return self._active_scrapers[index]
		except:
			return None
	
	def _enable_scrapers(self):
		for index in range(0, len(self.active_scrapers)):
			self.enabled_scrapers += 1
		
	def put_scraper(self, name, scraper):
		if not scraper.broken:
			self.active_scrapers.append(name)
			self._active_scrapers.append(scraper)
		
	def process_results(self, results):
		if self.show_scraper_progress and self.PB:
			self.PB.results += len(results)
			self.PB.next('Found [COLOR yellow]%s[/COLOR] new sources, %s total' % (len(results), self.PB.results))
		if self.cache_results:
			values =[]
			for r in results:
				try:
					values.append((self.hashid, r.service, self.clean_hostname(r.hostname), r.format(), r.quality, r.url, r.debrid, r.alldebrid, r.realdebrid, r.rpnet, r.premiumize))
				except: pass
			#values = [(self.hashid, r.service, r.hostname.strip(' \t\n\r'), r.format(), r.quality, r.url, r.debrid, r.alldebrid, r.realdebrid, r.rpnet, r.premiumize) for r in results]
			if DB_TYPE == 'mysql':
				TDB=MyDatabaseAPI(DB_ADDRESS, DB_NAME, DB_USER, DB_PASS, DB_PORT, init_flag='database_mysql_init.cache',quiet=True)
			else:
				TDB = MyDatabaseAPI(DB_FILE, init_flag='database_sqlite_init.cache',quiet=True)
			TDB.execute_many("INSERT INTO search_cache(hash, service, host, display, quality, url, debrid) VALUES(?,?,?,?,?,?,?)", values)
			TDB.commit()
			TDB.disconnect()
			del TDB
		self.search_results += results
		
	def search_tvshow(self, showname, season, episode, year=None, imdb_id=None, tvdb_id=None, return_sources=False):
		DB.connect()
		if self.cache_results:	
			self.hashid = hashlib.md5(showname+str(season)+str(episode)).hexdigest()
			DB.execute("DELETE FROM search_cache WHERE search_cache.cache_id in (select cache_id FROM stale_cache)")
			DB.commit()
		#self.result_stats = DB.query("SELECT service, host, attempts, success, ROUND (success / attempts * 100 ) AS percent FROM scraper_stats", force_double_array=True)
		self._get_active_resolvers()
		args = {"showname": showname, "season": season, "episode": episode, "year": year, "domains": self.domains, "imdb_id": imdb_id, "tmdb_id": tvdb_id}
		workers = ThreadPool(self.threadpool_size)
		if self.show_scraper_progress:
			self.PB = ProgressBar()
			self.PB.new('Searching for TV Sources', self.enabled_scrapers)
			self.PB.results = 0
		for index in range(0, self.enabled_scrapers):
			service = self.get_scraper_by_index(index).service
			if self.cache_results and  self.get_scraper_by_index(index).is_cachable:
				SQL = '''SELECT hashid, service, host, title, url, quality, debrid, alldebrid, realdebrid, rpnet, premiumize FROM fresh_cache WHERE hashid=? AND service=?'''
				cached = DB.query_assoc(SQL, [self.hashid, service], force_double_array=True)
			else:
				cached = False
			if cached:
				if self.show_scraper_progress and self.PB:
					self.PB.results += len(cached)
					self.PB.next('Found [COLOR yellow]%s[/COLOR] cached sources, %s total' % (len(cached), self.PB.results))
				self.search_results += cached
			else:
				if 'search_tvshow' in dir(self.get_scraper_by_index(index)):
					add_task = True
					if self.get_scraper_by_index(index).require_auth and (ADDON.get_setting(service + '_username') == '' or ADDON.get_setting(service + '_password') == ''): add_task = False
					if add_task: workers.queueTask(self.get_scraper_by_index(index).search_tvshow, args=args, taskCallback=self.process_results)
		workers.joinAll()
		resolved_url = None
		DB.disconnect()
		if return_sources:
			return self.process_sources(self)
		else:
			raw_url =  self.select_stream()
			if raw_url:
				resolved_url = self.resolve_url(raw_url)
			return resolved_url	
	
	def search_movie(self, title, year, imdb_id=None, tmdb_id=None, return_sources=False):
		DB.connect()
		if self.cache_results:
			self.hashid = hashlib.md5(title+str(year)).hexdigest()
			DB.execute("DELETE FROM search_cache WHERE search_cache.cache_id in (select cache_id FROM stale_cache)")
			DB.commit()
		#self.result_stats = DB.query("SELECT service, host, attempts, success, ROUND((success/attempts) * 100) AS score FROM scraper_stats", force_double_array=True)
		self._get_active_resolvers()
		args = {"title": title, "year": year, "domains": self.domains, "imdb_id": imdb_id, "tmdb_id": tmdb_id}
		workers = ThreadPool(self.threadpool_size)
		if self.show_scraper_progress:
			self.PB = ProgressBar()
			self.PB.new('Searching for Movie Sources', self.enabled_scrapers)
			self.PB.results = 0
		for index in range(0, self.enabled_scrapers):
			service = self.get_scraper_by_index(index).service
			if self.cache_results:
				SQL = '''SELECT hashid, service, host, title, url, quality FROM fresh_cache WHERE hashid=? AND service=?'''
				cached = DB.query_assoc(SQL, [self.hashid, service], force_double_array=True)
			else:
				cached = False	
			if cached:
				if self.show_scraper_progress and self.PB:
					self.PB.results += len(cached)
					self.PB.next('Found [COLOR yellow]%s[/COLOR] cached sources, %s total' % (len(cached), self.PB.results))
				self.search_results += cached
			else:
				if 'search_movie' in dir(self.get_scraper_by_index(index)):
					add_task = True
					if self.get_scraper_by_index(index).require_auth and (ADDON.get_setting(service + '_username') == '' or ADDON.get_setting(service + '_password') == ''): add_task = False
					if add_task: workers.queueTask(self.get_scraper_by_index(index).search_movie, args=args, taskCallback=self.process_results)
		workers.joinAll()
		resolved_url = None
		DB.disconnect()
		if return_sources:
			return self.process_sources(self)
		else:
			raw_url =  self.select_stream()
			if raw_url:
				resolved_url = self.resolve_url(raw_url)
			return resolved_url
	
	def _get_active_resolvers(self):
		self.domains = []
		try:
			for resolver in urlresolver.UrlResolver.implementors():
				for domain in resolver.domains:
					if re.match('^(.+?)\.(.+?)$', domain): self.domains.append(domain)
		except:
			self.domains = None

	def resolve_url(self, raw_url):
		test = re.search("^(.+?)(://)(.+?)$", raw_url)
		scraper = test.group(1)
		raw_url = test.group(3)

		if 'get_resolved_url' in dir(self.get_scraper_by_name(scraper)):
			resolved_url = self.get_scraper_by_name(scraper).get_resolved_url(raw_url)
			return resolved_url
		else:
			return self.do_urlresolver(raw_url)

	
	def do_urlresolver(self, raw_url):
		try:
			source = urlresolver.HostedMediaFile(url=raw_url)
			resolved_url = source.resolve() if source else None
			return resolved_url
		except Exception, e:
			ADDON.log(e)
			ADDON.raise_notify('UrlResolver Error.', str(e).replace(",", ''))
			return None

	def process_sources(self, sort=True):
		DB.connect()
		streams = []
		options = []
		disabled = []
		rankings = {}
		if self.show_scraper_progress and self.PB:
			self.PB.update_subheading('Processing results...')
			
		def get_score(hostname, service):
			for test in self.result_stats:
				if test[0] == service and test[1] == hostname:
					return test[4]
			return 0
		
		
		def get_rank(hostname):
			try:
				return rankings[hostname]
			except:
				return 0
		#ADDON.get_setting('custom_result_sorting')
		if ADDON.get_setting('enable_result_sorting') == 'true' and ADDON.get_setting('custom_result_sorting') == '1':
			def sort_streams(record):
				try:
					debrid = record.debrid
					rank = get_rank(record.hostname)
					hostname = record.hostname
					quality = record.quality
				except:
					debrid = record['debrid']
					rank = get_rank(record['host'])
					hostname = record['host']
					quality = record['quality']
					
				return (quality, rank, debrid, hostname)
				
		elif ADDON.get_setting('enable_result_sorting') == 'true' and ADDON.get_setting('custom_result_sorting') == '2':
			def sort_streams(record):
				try:
					debrid = record.debrid
					rank = get_rank(record.hostname)
					hostname = record.hostname
					quality = record.quality
				except:
					debrid = record['debrid']
					rank = get_rank(record['host'])
					hostname = record['host']
					quality = record['quality']
					
				return (debrid, rank, quality, hostname)
		else:	
			def sort_streams(record):
				try:
					rank = get_rank(record.hostname)
					hostname = record.hostname
					quality = record.quality
				except:
					rank = get_rank(record['host'])
					hostname = record['host']
					quality = record['quality']
					
				return (quality, rank, hostname)
		
		if sort:
			rows = DB.query("SELECT host, rank FROM host_ranks", force_double_array=True)
			for r in rows: rankings[r[0]] = r[1]
			rows = DB.query("SELECT host FROM host_weights WHERE disabled=1", force_double_array=True)
			disabled = [r[0] for r in rows]
			self.search_results.sort(reverse=True, key=lambda k: sort_streams(k))
		hosts = []
		for result in self.search_results:
			if isinstance(result, int): continue
			elif isinstance(result, dict):
				display = result['title']
				url = result['url']
				hostname = result['host']
				service = result['service']
				quality = result['quality']
				alldebrid = result['alldebrid']
				realdebrid = result['realdebrid']
				rpnet = result['rpnet']
				premiumize = result['premiumize']
			else:
				try:
					display = result.format()
					url = result.url
					hostname = result.hostname
					service = result.service
					quality = result.quality
					alldebrid = result.alldebrid
					realdebrid = result.realdebrid
					rpnet = result.rpnet
					premiumize = result.premiumize
				except Exception, e:
					ADDON.log("Sort Error: %s" % str(e))
					continue

			if hostname in disabled:
				continue
			
			if self.filters:
				if QUALITY.r_map[quality] not in self.filters: continue
				
				if realdebrid:
					if 'RealDebrid' not in self.filters:
						if not alldebrid and not rpnet and not premiumize: continue
				
				if alldebrid:
					if 'AllDebrid' not in self.filters:
						if not realdebrid and not rpnet and not premiumize: continue
						
				if rpnet:
					if 'Premiumize.ME' not in self.filters:
						if not realdebrid and not alldebrid and not premiumize: continue
				
				if premiumize:
					if 'RPNET' not in self.filters:
						if not realdebrid and not alldebrid and not rpnet: continue		
			
			hosts.append([hostname])
			streams.append(display)
			options.append(url)
		if DB_TYPE == 'mysql':
			SQL = "INSERT IGNORE INTO host_weights(host) VALUES(?)"
		else:
			SQL = "INSERT INTO host_weights(host) VALUES(?)"	
		DB.execute_many(SQL, hosts)
		DB.commit()
		DB.disconnect()
		return streams, options, self.search_results
	
	def select_stream(self, sort=True):
		streams, options, results = self.process_sources(sort)
		if self.PB: self.PB.close()
		if len(streams) == 0:
			ADDON.raise_notify('No results found.', 'No results, try changing your scraper set.')
			return False
		dialog = xbmcgui.Dialog()
		select = dialog.select("Select a stream", streams)
		if select < 0:
			return False

		return options[select]
	
	def update_success(self, hostname, service):
		SQL = '''
			UPDATE scraper_stats SET success = success + 1 WHERE service=? AND host=?
		'''
		DB.connect()
		DB.execute(SQL, [service, hostname])
		DB.commit()
		DB.disconnect()
		
	def test_quality(self, string, default=QUALITY.UNKNOWN):
		if re.search('1080p', string, re.IGNORECASE): return QUALITY.HD1080
		if re.search('720p', string, re.IGNORECASE): return QUALITY.HD720
		if re.search('480p', string, re.IGNORECASE): return QUALITY.SD480
		if re.search('(320p)|(240p)', string, re.IGNORECASE): return QUALITY.LOW
		return default
	
	def test_gv_quality(self, stream_url, default=QUALITY.HIGH):
		if 'itag=18' in stream_url or '=m18' in stream_url or stream_url.endswith('m18'):
			return QUALITY.LOW
		elif 'itag=22' in stream_url or '=m22' in stream_url or stream_url.endswith('m22'):
			return QUALITY.HD720
		elif 'itag=34' in stream_url or '=m34' in stream_url or stream_url.endswith('m34'):
			return QUALITY.HIGH
		elif 'itag=35' in stream_url or '=m35' in stream_url or stream_url.endswith('m35'):
			return QUALITY.HIGH
		elif 'itag=37' in stream_url or '=m37' in stream_url or stream_url.endswith('m37'):
			return QUALITY.HD1080
		else:
			return default
	
	def test_width_quality(self, width):
		width = int(width)
		if width > 1280:
			return QUALITY.HD1080
		elif width > 800:
			return QUALITY.HD720
		elif width > 640:
			return QUALITY.HIGH
		elif width > 320:
			return QUALITY.SD480
		
		return QUALITY.LOW
	
	def test_height_quality(self, height):
		height = int(height)
		if height > 900:
			return QUALITY.HD1080
		if height > 700:
			return QUALITY.HD720
		if height > 500:
			return QUALITY.HIGH
		elif height > 320:
			return QUALITY.SD480
		return QUALITY.LOW
	
	def set_color(self, text, color):
		return "[COLOR %s]%s[/COLOR]" % (color, text)
	
	def format_size(self, size):
		size = int(size) / (1024 * 1024)
		if size > 2000:
			size = size / 1024
			unit = 'GB'
		else :
			unit = 'MB'
		size = "%s %s" % (size, unit)
		return size
		
	
	def request(self, uri, params=None, query=None, headers=None, timeout=None, return_soup=False, return_json=False, append_base=True, get_redirect=False):
		COOKIE_JAR = vfs.join(COOKIE_PATH,self.service + '.lwp')
		net = NetLib(cookie_file=COOKIE_JAR)
		net._cjf = COOKIE_JAR
		net.get_redirect = get_redirect
		#net.set_cookies(COOKIE_JAR)
		if headers:
			if 'Referer' not in headers.keys(): 
				headers['Referer'] = self.referrer
			if 'Accept' not in headers.keys():	
				headers['Accept'] = self.accept
			if 'User-Agent' not in headers.keys():
				headers['User-Agent'] = self.get_user_agent()
		else:
			headers = {
			'Referer': self.referrer,
			'Accept': self.accept,
			'User-Agent': self.user_agent
			}	
		if query:
			uri += "?" + urllib.urlencode(query)
		if append_base:
			url = urljoin(self.base_url, uri)
		else:
			url = uri
		if timeout is None:
			timeout = self.timeout
		if params:
			html = net.post(url, params, headers=headers, timeout=timeout)
		else:
			html = net.get(url, headers=headers, timeout=timeout)
		net.save_cookies(COOKIE_JAR)
		if return_soup:
			return BeautifulSoup(html)
		elif return_json:
			return json.loads(html)
		else: 
			return html
				
	def get_redirect(self, uri, append_base=True):
		from dudehere.routines import httplib2
		h = httplib2.Http()
		h.follow_redirects = True
		return
		if append_base:
			(response, body) = h.request(self.base_url + uri)
		else:
			(response, body) = h.request(uri)
		return response['content-location']
			