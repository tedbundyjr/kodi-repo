import os
import sys
import re
import json
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import urllib
import unicodedata
import random
from xml.etree import ElementTree as ET
from dudehere.routines import *
from dudehere.routines.i18nlib import i18n
from dudehere.routines.vfs import VFSClass
vfs = VFSClass()

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
		schema = vfs.join(root, 'resources/database/schema.%s.sql' % self.db_type)
		if vfs.exists(schema):
			full_sql = vfs.read_file(schema)
			sql_stmts = full_sql.split(';')
			for SQL in sql_stmts:
				if SQL is not None and len(SQL.strip()) > 0:
					self.execute(SQL)
		ADDON.set_setting(self.init_flag, 'true')

if DB_TYPE == 'mysql':
	DB=MyDatabaseAPI(DB_ADDRESS, DB_NAME, DB_USER, DB_PASS, DB_PORT, init_flag='database_mysql_init.cache', connect=False)
else:
	DB = MyDatabaseAPI(DB_FILE, init_flag='database_sqlite_init.cache', connect=False)


VIEWS = enum(DEFAULT=500, LIST=50, BIGLIST=51, THUMBNAIL=500, SMALLTHUMBNAIL=522, FANART=508, POSTERWRAP=501, MEDIAINFO=504, MEDIAINFO2=503, MEDIAINFO3=515, WIDE=505, LIST_DEFAULT=50, TV_DEFAULT=50, MOVIE_DEFAULT=50, SEASON_DEFAULT=50, EPISODE_DEFAULT=50)
	

class ContextMenu:
	def __init__(self):
		self.commands = []

	def add(self, text, arguments={}, script=False, visible=True):
		if hasattr(visible, '__call__'):
			if visible() is False: return
		else:
			if visible is False: return
		if isinstance( text, ( int, long ) ):
			text = i18n(text)
		cmd = self._build_url(arguments, script)
		self.commands.append((text, cmd, ''))
	
	def _build_url(self, arguments, script):
		try:
			plugin_url =  "%s?%s" % (ADDON_URL, urllib.urlencode(arguments))
		except UnicodeEncodeError:
			for k in arguments:
				if isinstance(arguments[k], unicode):
					arguments[k] = arguments[k].encode('utf-8')
			plugin_url =  "%s?%s" % (ADDON_URL, urllib.urlencode(arguments))
			
		if script:
			cmd = 'XBMC.RunPlugin(%s)' % (plugin_url)
		else:
			cmd = "XBMC.Container.Update(%s)" % plugin_url
		return cmd

	def get(self):
		return self.commands


class Plugin():
	__percent = 0
	__current_time = 0
	__total_time = 0
	VIEWS = False
	default_context_menu_items = []
	def __init__(self, enable_default_views=True, replace_context_menu=False, default_views=False):
		self.args = ADDON.parse_query(sys.argv[2])
		self.dispatcher = {}
		self.kargs = {}
		self.ENABLE_DEFAULT_VIEWS = enable_default_views
		if default_views:
			self.VIEWS = default_views
		self.replace_context_menu_by_default = replace_context_menu
		if self.args['mode'] is None:
			self.mode='main'
		else:
			self.mode = self.args['mode']
		
		self.DB = DB
	
	def arg(self, k, default=None):
		if k in self.args.keys():
			v = self.args[k]
			if v == '': return default
			if v == 'None': return default
			return v
		else:
			return default
	
	def get_arg(self, k, default=None):
		return self.arg(k, default)
	
	def check_version(self, previous, current):
		if not re.search('\d+\.\d+\.\d+', str(previous)): return True
		p = previous.split('.')
		c = current.split('.')	
		# test major version
		if int(p[0]) < int(c[0]): return True
		# test minor version
		if int(p[1]) < int(c[1]): return True
		# test sub minor version
		if int(p[2]) < int(c[2]): return True
		return False
	
	def normalize(self, string):
		return unicodedata.normalize('NFKD',unicode(string.encode('utf-8'))).encode('utf-8','ignore')
		
	def register(self, mode, target, kargs=None):
		if isinstance(mode, list):
			for foo in mode:
				self.dispatcher[foo] = target
				self.kargs[foo] = kargs
		else:
			self.dispatcher[mode] = target
			self.kargs[mode] = kargs
		
	def run(self):
		if ADDON.get_setting('setup_run') != 'true':
			ADDON.log("First Run", LOG_LEVEL.VERBOSE)
			self.first_run()
		elif self.check_version(ADDON.get_setting('version'), str(VERSION)):
			self.update_run()	
			
		if self.kargs[self.args['mode']] is None:

			self.dispatcher[self.args['mode']]()

		else:
			self.dispatcher[self.args['mode']](*self.kargs[self.args['mode']])
		ADDON.log("Executing with args: %s" % self.args, LOG_LEVEL.VERBOSE)
		
	def first_run(self):
		pass
	
	def update_run(self):
		pass
	
	def initialize_settings(self, upgrade=False):
		if not vfs.exists(DATA_PATH): vfs.mkdir(DATA_PATH)
		xml_in = vfs.join(ROOT_PATH, 'resources/settings.xml')
		xml_out = vfs.join(DATA_PATH, 'settings.xml')
		soup_in = vfs.read_file(xml_in, soup=True)
		document = ET.Element("settings")
		settings = soup_in.findAll('setting')
		for setting in settings:
			try:
				id = setting['id']
				if upgrade and ADDON.get_setting(id):
					default = ADDON.get_setting(id)
				else:
					default = setting['default']
				node = ET.SubElement(document, 'setting', id=id, default=default)
			except:
				pass
		et = ET.ElementTree(document)
		et.write(xml_out)
		
	def set_default_context_menu(self, items):
		self.default_context_menu_items = items
		
	def add_menu_item(self, query, infolabels, total_items=0, image='', fanart='', menu=None, replace_menu=None, visible=True):
		if hasattr(visible, '__call__'):
			if visible() is False: return
		else:
			if visible is False: return
		if isinstance( infolabels['title'], ( int, long ) ):
			infolabels['title'] = i18n(infolabels['title'])
		if replace_menu is None:
			replace_menu = self.replace_context_menu_by_default
		if menu is None:
			menu = ContextMenu()
		for m in self.default_context_menu_items:
			menu.add(*m)
		if not fanart:
			fanart = ROOT_PATH + '/fanart.jpg'

		listitem = xbmcgui.ListItem(infolabels['title'], iconImage=image, thumbnailImage=image)
		listitem.setInfo('video', infolabels)
		listitem.setProperty('IsPlayable', 'false')
		listitem.setProperty('fanart_image', fanart)
		if menu:
			listitem.addContextMenuItems(menu.get(), replaceItems=replace_menu)
		plugin_url = self.build_plugin_url(query)
		xbmcplugin.addDirectoryItem(HANDLE_ID, plugin_url, listitem, isFolder=True, totalItems=total_items)

	
	def add_video_item(self, query, infolabels, total_items=0, image='', fanart='', menu=None, replace_menu=None, set_resume=False):
		listitem = xbmcgui.ListItem(infolabels['title'], iconImage=image, thumbnailImage=image)
		listitem.setInfo("video", infolabels)
		listitem.setProperty('IsPlayable', 'true')
		listitem.setProperty('fanart_image', fanart)
		if set_resume:
			listitem.setProperty('totaltime', '999999')
			listitem.setProperty('resumetime', str(set_resume))
			listitem.setProperty('percentplayed', '10')
		else:
			listitem.setProperty('totaltime', '0')
			listitem.setProperty('resumetime', '0')
			listitem.setProperty('percentplayed', '0')

		if replace_menu is None:
			replace_menu = self.replace_context_menu_by_default
		if menu is None:
			menu = ContextMenu()
		for m in self.default_context_menu_items:
			menu.add(*m)	
		if menu:
			listitem.addContextMenuItems(menu.get(), replaceItems=replace_menu)
		query['rand'] = random.random()
		plugin_url = self.build_plugin_url(query)
		xbmcplugin.addDirectoryItem(HANDLE_ID, plugin_url, listitem, isFolder=False, totalItems=total_items)
		
	def build_plugin_url(self, arguments):
		try:
			plugin_url = "%s?%s" % (ADDON_URL, urllib.urlencode(arguments))
		except UnicodeEncodeError:
			for k in arguments:
				if isinstance(arguments[k], unicode):
					arguments[k] = arguments[k].encode('utf-8')
			plugin_url = "%s?%s" % (ADDON_URL, urllib.urlencode(arguments))		
		return plugin_url
	
	def execute_query(self, query):
		plugin_url = self.build_plugin_url(query)
		self.execute_url(plugin_url)
	
	def execute_url(self, plugin_url):
		cmd = 'XBMC.RunPlugin(%s)' % (plugin_url)
		self.run_command(cmd)
	
	def navigate_to(self, query):
		plugin_url = self.build_plugin_url(query)
		self.go_to_url(plugin_url)
		
	def go_to_url(self, plugin_url):
		cmd = "XBMC.Container.Update(%s)" % plugin_url
		xbmc.executebuiltin(cmd)
	
	def run_command(self, cmd):
		xbmc.executebuiltin(cmd)
	
	def play_url(self, plugin_url):
		cmd = 'XBMC.PlayMedia(%s)' % (plugin_url)
		self.run_command(cmd)
		
	def eod(self, view=None, content=None, viewid=None, clear_search=False):
		if self.VIEWS and view is None:
			view = self.VIEWS.DEFAULT
		elif view is None:
			view = VIEWS.DEFAULT
		if view=='custom':
			self.set_view('custom', content=content, viewid=viewid)
		else:
			self.set_view(view,content=content)
		if clear_search:
			self.clear_property('search.query')
			self.clear_property('search.query.refesh')
		xbmcplugin.endOfDirectory(HANDLE_ID)
	
	def set_view(self, view, content=None, viewid=None):
		if self.ENABLE_DEFAULT_VIEWS:
			if content:
				xbmcplugin.setContent(int(sys.argv[1]), content)
			if not viewid:
				viewid = view
			xbmc.executebuiltin("Container.SetViewMode(%s)" % viewid)
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
			xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )	
	
	def dialog_input(self, title):
		kb = xbmc.Keyboard('', title, False)
		kb.doModal()
		if (kb.isConfirmed()):
			text = kb.getText()
			if text != '':
				return text
		return None	
	
	def dialog_number(self, title, default=''):
		dialog = xbmcgui.Dialog()
		r = dialog.numeric(0, title, default)
		return r
	
	def show_textbox(self, heading, content):
		TextBox().show(heading, content)
	
	def dialog_ok(self, title="", m1="", m2="", m3=""):
		dialog = xbmcgui.Dialog()
		dialog.ok(title, m1, m2, m3)
	
	def confirm(self, title, m1='', m2='', m3='', yes='', no=''):
		dialog = xbmcgui.Dialog()
		return dialog.yesno(title, m1, m2, m3, no, yes)
	
	def dialog_select(self, heading, options):
		dialog = xbmcgui.Dialog()
		index = dialog.select(heading, options)
		if index >= 0:
			return index
		else: 
			return False
	
	def notify(self, title, message, timeout=1500, image=vfs.join(ROOT_PATH, 'icon.png')):
		cmd = "XBMC.Notification(%s, %s, %s, %s)" % (title, message, timeout, image)
		xbmc.executebuiltin(cmd)
		
	def error_message(self, title, message, timeout=2500, image=vfs.join(ROOT_PATH, 'icon.png')):
		cmd = "XBMC.Notification(%s, %s, %s, %s)" % (title, message , timeout, image)
		xbmc.executebuiltin(cmd)	
		
	def refresh(self, plugin_url=None):
		query = self.get_property('search.query')
		if query:
			self.set_property('search.query.refesh', query)
			self.clear_property('search.query')
			
		if plugin_url is None:
			xbmc.executebuiltin("Container.Refresh")
		else:
			xbmc.executebuiltin("Container.Refresh(%s)" % plugin_url)
			
	def exit(self):
		exit = xbmc.executebuiltin("XBMC.ActivateWindow(Home)")
		return exit
	
	def kodi_json_request(self, method, params):
		jsonrpc =  json.dumps({ "jsonrpc": "2.0", "method": method, "params": params, "id": 1 })
		response = json.loads(xbmc.executeJSONRPC(jsonrpc))
		return response
	
	def get_fileid(self, path=None):
		prams = {"file": "path"}
		response = self.kodi_json_request('Files.GetFileDetails', params)
		ADDON.log( response )
		
	def get_movieid(self, title, year):
		params = { "filter": {"and": [
			{"field": "title", "operator": "is", "value": str(title)},
			{"field": "year", "operator": "is", "value": str(year)}
		]}}
		response = self.kodi_json_request('Files.GetMovies', params)
		try:
			return response['result']['movies'][0]['movieid']
		except:
			return False

	def get_episodeid(self, show_title, season, episode):
		params = { "filter": {"and": [
			{"field": "tvshow", "operator": "is", "value": show_title}, 
			{"field": "season", "operator": "is", "value": str(season)}, 
			{"field": "episode", "operator": "is", "value": str(episode)}
		]}, "properties": ["playcount"]}
		response = self.kodi_json_request('VideoLibrary.GetEpisodes', params)
		ADDON.log(response)
		try:
			return response['result']['episodes'][0]['episodeid']
		except:
			return False
	
	def get_movie_playcount(self, movie, year):
		params = { "filter": {"and": [
			{"field": "title", "operator": "is", "value": movie},
			{"field": "year", "operator": "is", "value": str(year)}
		]}, "properties": ["playcount"]}
		response = self.kodi_json_request('VideoLibrary.GetMovies', params)
		try:
			return response['result']['movies'][0]['movieid'],response['result']['movies'][0]['playcount']
		except:
			return False,False
	
	def get_episode_playcount(self, show_title, season, episode):
		params = { "filter": {"and": [
			{"field": "tvshow", "operator": "is", "value": show_title}, 
			{"field": "season", "operator": "is", "value": str(season)}, 
			{"field": "episode", "operator": "is", "value": str(episode)}
		]}, "properties": ["playcount"]}
		response = self.kodi_json_request('VideoLibrary.GetEpisodes', params)
		try:
			return response['result']['episodes'][0]['episodeid'], response['result']['episodes'][0]['playcount']
		except:
			return False,False
	
	def set_resume_point(self, imdb_id, seconds, season=0, episode=0):
		DB.connect()
		DB.execute("REPLACE INTO playback_states(imdb_id, season, episode, current) VALUES(?,?,?,?)", [imdb_id, season, episode, seconds])
		DB.commit()
		DB.disconnect()

	def get_resume_point(self, imdb_id, season=None, episode=None):
		DB.connect()
		resume = DB.query("SELECT current FROM playback_states WHERE imdb_id=? AND season=? AND episode=?", [imdb_id, season, episode])
		DB.disconnect()
		resume_point = False
		
		if resume:
			seconds = float(resume[0])
			if seconds < 60:
				return resume_point
			c = self.confirm("Resume Playback?", "Resume playback from %s" % self.format_time(seconds), yes='Start from beginning', no='Resume') == 0
			if c:
				resume_point = int(seconds)
		return resume_point
	
	def format_time(self, seconds):
		seconds = int(seconds)
		minutes, seconds = divmod(seconds, 60)
		if minutes > 60:
			hours, minutes = divmod(minutes, 60)
			return "%02d:%02d:%02d" % (hours, minutes, seconds)
		else:
			return "%02d:%02d" % (minutes, seconds)
	
	def clear_resume_point(self, imdb_id, season=None, episode=None):
		DB.connect()
		DB.execute("DELETE FROM playback_states WHERE imdb_id=? AND season=? AND episode=?", [imdb_id, season, episode])
		DB.commit()
		DB.disconnect()
	
	def play_stream(self, url,  metadata={"cover_url": "", "title": ""}, title=None):
		if title is None: title = metadata['title']
		listitem = xbmcgui.ListItem(title, iconImage=metadata['cover_url'], thumbnailImage=metadata['cover_url'], path=url)
		listitem.setProperty('IsPlayable', 'true')
		listitem.setPath(url)
		listitem.setInfo("video", metadata)
		win = xbmcgui.Window(10000)
		win.setProperty('GenericPlaybackService.playing', "true")
		if 'imdb_id' in metadata or 'imdb' in metadata:
			if 'season' in metadata:
				resume_point = self.get_resume_point(metadata['imdb_id'], metadata['season'], metadata['episode'])
			else:
				resume_point = self.get_resume_point(metadata['imdb_id'])
			if resume_point:
				listitem.setProperty('totaltime', '999999')
				listitem.setProperty('resumetime', str(resume_point))
		try:
			xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem)
		except Exception, e:
			ADDON.log( e )
		#delta = 0
		while win.getProperty('GenericPlaybackService.playing') == "true":
			xbmc.sleep(100)
			"""delta += 100
		if delta > 6000:
			from dudehere.routines.scrapers import CommonScraper
			Scraper = CommonScraper(load=False)
			Scraper.update_success(self.get_property('hostname'), self.get_property('service'))
		self.clear_property('hostname')
		self.clear_property('service')"""
		self.__on_stream_stop()

	def __on_stream_stop(self):
		self.on_playback_stop()
		
	def get_property(self, k):
		p = xbmcgui.Window(10000).getProperty('GenericPlaybackService.' + k)
		if p == 'false': return False
		if p == 'true': return True
		return p
	
	def set_property(self, k, v):
		xbmcgui.Window(10000).setProperty('GenericPlaybackService.' + k, v)
	
	def clear_property(self, k):
		xbmcgui.Window(10000).clearProperty('GenericPlaybackService.' + k)
		
	def show_window(self, window_id):
		xbmcgui.Window(window_id).show()

	def hide_window(self, window_id):
		xbmcgui.Window(window_id).close()
	
	def window_exists(self, window_id):
		try:
			xbmcgui.Window(window_id)
			return True
		except:
			return False
		
	def get_stream_stop_times(self):
		win = xbmcgui.Window(10000)
		percent = win.getProperty('GenericPlaybackService.percent')
		current_time = win.getProperty('GenericPlaybackService.current_time')
		total_time = win.getProperty('GenericPlaybackService.total_time')
		return {"percent": int(percent), "current": current_time, "total": total_time}
	
	def on_playback_stop(self):
		'''*
		Overide this function with whatever you want to happen once playback has finished
		*'''
		pass

class ProgressBar(xbmcgui.DialogProgress):
	def __init__(self, *args, **kwargs):
		xbmcgui.DialogProgress.__init__(self, *args, **kwargs)
		self._silent = False
		self._index = 0
		self._total = 0
		self._percent = 0
		
	def new(self, heading, total):
		if not self._silent:
			self._index = 0
			self._total = total
			self._percent = 0
			self._heading = heading
			self.create(heading)
			self.update(0, heading, '')
	def update_subheading(self, subheading):
		self.update(self._percent, self._heading, subheading)
		
	def next(self, subheading):
		if not self._silent:
			self._index = self._index + 1
			self._percent = self._index * 100 / self._total
			self.update(self._percent, self._heading, subheading)
		
class TextBox:
	# constants
	WINDOW = 10147
	CONTROL_LABEL = 1
	CONTROL_TEXTBOX = 5

	def __init__( self, *args, **kwargs):
		# activate the text viewer window
		xbmc.executebuiltin( "ActivateWindow(%d)" % ( self.WINDOW, ) )
		# get window
		self.window = xbmcgui.Window( self.WINDOW )
		# give window time to initialize
		xbmc.sleep( 500 )


	def setControls( self ):
		#get header, text
		heading, text = self.message
		# set heading
		self.window.getControl( self.CONTROL_LABEL ).setLabel( "%s - %s v%s" % ( heading, ADDON_NAME, VERSION) )
		# set text
		self.window.getControl( self.CONTROL_TEXTBOX ).setText( text )

	def show(self, heading, text):
		# set controls

		self.message = heading, text
		self.setControls()		