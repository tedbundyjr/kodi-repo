import urllib2, urllib
import socket
from urllib2 import URLError, HTTPError
from datetime import datetime
import re, time
import json
import hashlib
import base64
import traceback

from dudehere.routines import *
from dudehere.routines.omdbapi import OMDBapi
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
BASE_URL = "http://api-v2launch.trakt.tv"
CLIENT_ID = ADDON.get_setting('trakt_client_id')
SECRET_ID = ADDON.get_setting('trakt_secret')
PIN_URL = ADDON.get_setting('trakt_pin_url')
DAYS_TO_GET = 21
DECAY = 2
from dudehere.routines import *
from dudehere.routines.vfs import VFSClass
from dudehere.routines.database import SQLiteDatabase as DatabaseAPI
vfs = VFSClass()
omdb = OMDBapi()

class MyDatabaseAPI(DatabaseAPI):
	def _initialize(self):
		do_init = True
		try:
			test = self.query("SELECT 1 FROM version WHERE db_version >= ?", [self.db_version])
			if test:
				do_init = False
		except:
			do_init = True
		if do_init:
			import xbmcaddon
			root = xbmcaddon.Addon('script.module.dudehere.routines').getAddonInfo('path')
			schema = vfs.join(root, 'resources/database/trakt.schema.sql')
			if vfs.exists(schema):
				full_sql = vfs.read_file(schema)
				sql_stmts = full_sql.split(';')
				for SQL in sql_stmts:
					if SQL is not None and len(SQL.strip()) > 0:
						self.execute(SQL)
						print SQL
				self.execute('INSERT OR REPLACE INTO version(db_version) VALUES(?)', [self.db_version])
				self.commit()
DB_LOCATION = vfs.join('special://userdata', 'addon_data/script.module.dudehere.routines')
if not vfs.exists(DB_LOCATION):
	vfs.mkdir(DB_LOCATION)
DB_FILE = vfs.join('special://userdata', 'addon_data/script.module.dudehere.routines/trakt.db')
DB = MyDatabaseAPI(DB_FILE, init_flag='database_sqlite_init.trakt', version_flag='database_sqlite_version.trakt', version=4, connect=True)


class TraktError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		try:
			s = self.value
		except Exception,e:
			print "-----",type(e),e
		return s
	
class TraktTempError(Exception):
	pass

class TraktAPI():
	def __init__(self):
		self.token = None
		self.timeout = 30
		self.limit = 100
	
	def authorize(self, pin):
		response = self._authorize(pin)
		return response
	
	def get_settings(self):
		uri = '/users/settings'
		settings = self._call(uri, auth=True)
		if not settings: return False
		return settings
	
	def get_object_id(self, trakt_id = None, imdb_id=None, tmdb_id=None, id_type='trakt'):
		if trakt_id is not None: return trakt_id
		if imdb_id is not None: return imdb_id
		uri = '/search'
		result = self._call(uri, params={"id_type": 'tmdb_id', "id": tmdb_id})
		if not result: return False
		type = result[0]['type']
		return result[0][type]['ids']['id_type']
	
	def resolve_imdb_id(self, title, year, media, tmdb_id='', trakt_id=''):
		imdb_id = None
		try:
			id = DB.query("SELECT imdb_id FROM id_cache WHERE title=? AND media=? AND year=?", [title, media, year])
			if id:
				imdb_id = id[0]
			else:
				imdb_id = omdb.query_id(title, year, media)
				if imdb_id is not None:
					DB.execute("INSERT INTO id_cache(title, year, media, imdb_id, tmdb_id, trakt_id) VALUES(?,?,?,?,?,?)", [title, year, media, imdb_id, tmdb_id, trakt_id])
					DB.commit()
		except Exception, e:
			ADDON.log(e)
		return imdb_id
	
	def query_id(self, id_type, id):
		uri = '/search'
		result = self._call(uri, params={"id_type": id_type, "id": id})
		if not result: return False
		type = result[0]['type']
		return result[0][type]['ids']['imdb']
	
	def query_slug(self, id_type, id):
		uri = '/search'
		result = self._call(uri, params={"id_type": id_type, "id": id})
		if not result: return False
		type = result[0]['type']
		return result[0][type]['ids']['slug']
	
	def lookup(self, media, id, id_type='imdb'):
		uri = '/search'
		record = self._call(uri, params={"id_type": id_type, "id": id, 'extended': 'full,images'})
		if not record: return False
		metadata = self.process_record(record, media)
		return metadata
	
	def get_episode_details(self, id, season, episode, params={'extended': 'full,images'}):
		uri = '/shows/%s/seasons/%s/episodes/%s' % (id, season, episode)
		episode = self._call(uri, params=params, auth=False, cache='episode')
		show = self.get_show_details(id)
		record = {"episode": episode, "show": show}
		return self.process_record(record, media='episode')
	
	def get_show_details(self, id):
		uri = '/shows/%s' % id
		record = self._call(uri, params={'extended': 'full,images'}, auth=False, cache='show')
		return record
	
	def get_movie_details(self, id):
		uri = '/movies/%s' % (id)	
		record = self._call(uri, params={'extended': 'full,images'}, auth=False, cache='movie')
		if not record: return False
		return self.process_record(record, media='movie')
	
	def get_metadata(self, media, imdb_id, tmdb_id, trakt_id, season=None, episode=None):
		metadata = None
		if media == 'episode':
			return self.get_episode_metadata(imdb_id, tmdb_id, trakt_id, season, episode)
		elif media == 'tvshow':
			return metadata
		else:
			return self.get_movie_metadata(imdb_id, tmdb_id, trakt_id)
	
	def get_episode_metadata(self, imdb_id, tmdb_id, trakt_id, season, episode):
		metadata = None
		SQL = "SELECT * FROM episodes WHERE (imdb_id=? OR tmdb_id=? OR trakt_id=?) AND season=? AND episode=? LIMIT 1"
		cached = DB.query_assoc(SQL, [imdb_id, tmdb_id, trakt_id, season, episode])
		if cached:
			cached['cast'] = []

			return cached
		if trakt_id:
			return self.get_episode_details(trakt_id, season, episode)
		if imdb_id:
			return self.get_episode_details(imdb_id, season, episode)
		if tmdb_id:
			imdb_id = self.query_id('tmdb', tmdb_id)
			return self.get_episode_details(imdb_id, season, episode)
		return metadata
	
	def get_movie_metadata(self, imdb_id, tmdb_id, trakt_id):
		metadata = None
		SQL = "SELECT * FROM movies WHERE (imdb_id=? OR tmdb_id=? OR trakt_id=?) LIMIT 1"
		cached = DB.query_assoc(SQL, [imdb_id, tmdb_id, trakt_id])
		if cached:
			cached['cast'] = []
			return cached
		if imdb_id:
			return self.get_movie_details(imdb_id)
		if tmdb_id:
			imdb_id = self.query_id('tmdb', tmdb_id)
			return self.get_movie_details(imdb_id)
		if trakt_id:
			return self.get_movie_details(trakt_id)
		return metadata
		
	def search(self, query, media='show'):
		uri = '/search'
		return self._call(uri, params={'query': query, 'type': media, 'extended': 'full,images'}, cache=media)
		
	def get_calendar_shows(self):
		from datetime import date, timedelta
		d = date.today() - timedelta(days=(DAYS_TO_GET - 1)) 
		today = d.strftime("%Y-%m-%d")
		uri = '/calendars/my/shows/%s/%s' % (today, DAYS_TO_GET)
		media='episode'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=True)
	
	def get_calendar_daily_shows(self, delta=0, number=1):
		from datetime import date, timedelta
		d = date.today() - timedelta(days=delta)
		start_date = d.strftime("%Y-%m-%d")
		uri = '/calendars/my/shows/%s/%s' % (start_date, number)
		media='episode'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=True)
	
	def get_calendar_episodes(self, delta=0, number=1):
		from datetime import date, timedelta
		d = date.today() - timedelta(days=delta)
		start_date = d.strftime("%Y-%m-%d")
		uri = '/calendars/all/shows/%s/%s' % (start_date, number)
		media='episode'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_calendar(self, calendar, delta=0, number=1):
		from datetime import date, timedelta
		d = date.today() - timedelta(days=delta)
		start_date = d.strftime("%Y-%m-%d")
		uri = '/calendars/%s/%s/%s' % (calendar, start_date, number)
		media='episode'
		auth = calendar.startswith("my")
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=auth)
		
	def get_similar_tvshows(self, id):
		uri = '/shows/%s/related' % id
		media = 'show'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_collected_tvshows(self):
		uri = '/sync/collection/shows'
		media='show'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=True)
	
	def get_trending_tvshows(self):
		uri = '/shows/trending'
		media='show'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_anticipated_tvshows(self):
		uri = '/shows/anticipated'
		media='show'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_popular_tvshows(self):
		uri = '/shows/popular'
		media='show'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_recommended_tvshows(self):
		uri = '/recommendations/shows'
		media='show'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=True)
	
	def get_show_seasons(self, id):
		uri = '/shows/%s/seasons' % id
		media='season'
		return self._call(uri, params={'extended': 'images'}, cache=media)
	
	def get_show_episodes(self, id, season):
		uri = '/shows/%s/seasons/%s' % (id, season)
		media='episode'
		return self._call(uri, params={'extended': 'full,images'}, cache=media)
	
	def get_watchlist_tvshows(self, extended='full,images', simple=False, id_type='imdb'):
		uri = '/users/me/watchlist/shows'
		if simple:
			records = self._call(uri, auth=True, cache='watchlist')
			if not records: return []
			return [record['show']['ids'][id_type] for record in records]
		else:
			return self._call(uri, params={'extended': extended}, auth=True, cache='watchlist')
	
	def get_watchlist_movies(self, extended='full,images', simple=False, id_type='imdb'):
		uri = '/users/me/watchlist/movies'
		if simple:
			records = self._call(uri, auth=True, cache='watchlist')
			if not records: return []
			return [record['movie']['ids'][id_type] for record in records]
		else:
			return self._call(uri, params={'extended': extended}, auth=True, cache='watchlist')
	
	def get_collected_movies(self):
		uri = '/sync/collection/movies'
		media='movie'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=True)
	
	def get_trending_movies(self):
		uri = '/movies/trending'
		media='movie'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_popular_movies(self):
		uri = '/movies/popular'
		media = 'movie'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_recommended_movies(self):
		uri = '/recommendations/movies'
		media = 'movie'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=True)
	
	def get_similar_movies(self, id):
		uri = '/movies/%s/related' % id
		media = 'movie'
		return self._call(uri, params={'extended': 'full,images'}, cache=media, auth=False)
	
	def get_show_info(self, id, episodes=False):
		if episodes:
			uri = '/shows/%s/seasons' % id
			return self._call(uri, params={'extended': 'episodes,full'}, cache='show')
		else:
			uri = '/shows/%s' % id
			return self._call(uri)
	
	def get_custom_lists(self):
		uri = '/users/me/lists'
		results = self._call(uri, params={}, auth=True)
		if not results: return False
		return sorted(results)
	
	def get_liked_lists(self):
		uri = '/users/likes/lists'
		return sorted(self._call(uri, params={}, auth=True))
	
	def get_custom_list(self, slug, media, username=None, params={'extended': 'full,images'}):
		if media=='tvshows': media = 'show'
		if media=='tv': media = 'show'
		if username is None:	
			uri = '/users/me/lists/%s/items' % slug 
			auth = True
		else:
			uri = '/users/%s/lists/%s/items' % (username.replace('.', '-'), slug)
			auth = False
		temp = self._call(uri, params=params, auth=auth)
		results = []
		if not temp: return results
		for r in temp:
			if r['type'] == media:
				results.append(r)
		return results		
	
	def create_custom_list(self, title):
		uri = '/users/me/lists'
		post_dict = {
			"name": title,
			"description": "Created by %s" % ADDON_NAME,
			"privacy": "public",
			"display_numbers": True,
			"allow_comments": True
		}
		return self._call(uri, data=post_dict, auth=True)
	
	def add_to_watchlist(self, media, id, id_type='imdb'):
		uri = '/sync/watchlist'
		data = {media:  [{'ids': {id_type: id}}]}
		self._clear_watchlist_cache()
		return self._call(uri, data, auth=True)
	
	def delete_from_watchlist(self, media, id, id_type='imdb'):
		uri = '/sync/watchlist/remove'
		data = {media:  [{'ids': {id_type: id}}]}
		self._clear_watchlist_cache()
		return self._call(uri, data, auth=True)
		
	def add_to_custom_list(self, media, slug, id, id_type='imdb'):
		if media=='movie':
			post_dict = {'movies': [{'ids': {id_type: id}}]}
		else:
			post_dict = {'shows': [{'ids': {id_type: id}}]}
		uri = '/users/me/lists/%s/items' % slug
		return self._call(uri, data=post_dict, auth=True)
	
	def delete_from_custom_list(self, media, slug, id, id_type='imdb'):
		if media=='movie':
			post_dict = {'movies': [{'ids': {id_type: id}}]}
		else:
			post_dict = {'shows': [{'ids': {id_type: id}}]}
		uri = '/users/me/lists/%s/items/remove' % slug
		return self._call(uri, post_dict, auth=True)
	
	def delete_custom_list(self, slug):
		uri = '/users/me/lists/%s' % slug
		return self._delete(uri)
	
	def set_watched_state(self, media, id, watched, season=None):
		uri = '/sync/history' if watched else '/sync/history/remove'
		if media == 'episode':
			post_dict = {'episodes': [{"ids": {"trakt": id}}]}
		elif media == 'movie':
			post_dict = {'movies': [{"ids": {"imdb": id}}]}
		elif media == 'season':
			post_dict = {'shows': [{'seasons': [{'number': int(season)}], 'ids': {'imdb': id}}]}
		self._clear_watchlist_cache()
		return self._call(uri, post_dict, auth=True)
	
	def get_watched_history(self, media):
		uri = '/sync/watched/%s' % media
		if media == 'shows':
			results = {}
			response = self._call(uri, auth=True)
			if not response: return False
			for r in response:
				imdb_id =  r['show']['ids']['imdb']
				results[imdb_id] = {}
				seasons = r['seasons']
				for season in seasons:
					results[imdb_id][season['number']] = []
					for episode in season['episodes']: results[imdb_id][season['number']].append(episode['number'])
			return results
		else:
			results = {"imdb": [], "tmdb": [], "trakt": []}
			response = self._call(uri, auth=True)
			if not response: return False
			for r in response:
				results['trakt'].append(r['movie']['ids']['trakt'])
				results['imdb'].append(r['movie']['ids']['imdb'])
				results['tmdb'].append(r['movie']['ids']['tmdb'])
			return results	
	
	def get_next_episodes(self):
		uri = '/sync/history/episodes'
		response = self._call(uri, auth=True)
		if not response: return False
		for r in response:
			ADDON.log(r)
		#ADDON.log(response)
	
	def get_watched_episodes(self, id):
		uri = '/sync/history/seasons/%s' % id
		results = self._call(uri, auth=True)
		return results
	
	def get_bookmark(self, media, id, id_type = 'imdb', season=None, episode=None):
		bookmarks = self.get_bookmarks(media)
		for bookmark in bookmarks:
			if media == 'episodes':
				if id== bookmark['show']['ids'][id_type] and bookmark['episode']['season'] == int(season) and bookmark['episode']['number'] == int(episode):
					return bookmark['progress']
			else:
				if id == bookmark['movie']['ids'][id_type]:
					return bookmark['progress']
		return None
	def get_bookmarks(self, media):
		uri = '/sync/playback/%s' % media
		return self._call(uri, auth=True)
		
	
	def process_record(self, record, media=None, watched=None, show=None):
		if media=='movie':
			meta = self.process_movie(record)
			return meta
		elif media=='episode':
			meta = self.process_episode(record, watched=watched, show=show)
			return meta
		elif media=='tvshow':
			meta = self.process_show(record)
			return meta
	
	def meta_map(self, path, object, default=''):
		try:
			if isinstance(path, list):
				for k in path:
					object = object[k]
			else:
				object = object[path]
				object = object if object is not None else default
			return object
		except:
			return default
		
	
	def process_show(self, record):
		try:
			show = record['show']
		except:
			show = record
		meta = {}

		meta['imdb_id'] = self.meta_map(['ids', 'imdb'], show)
		meta['tvdb_id'] = self.meta_map(['ids', 'tvdb'], show)
		meta['tmdb_id'] = self.meta_map(['ids', 'tmdb'], show)
		meta['trakt_id'] = self.meta_map(['ids', 'trakt'], show)
		meta['slug'] = self.meta_map(['ids', 'slug'], show)
		meta['title'] = self.meta_map('title', show)
		meta['TVShowTitle'] = self.meta_map('title', show)
		meta['rating'] = self.meta_map('rating', show)
		meta['duration'] = self.meta_map('runtime', show)
		meta['plot'] = self.meta_map('overview', show)
		meta['mpaa'] = self.meta_map('certification', show)
		meta['premiered'] = self.meta_map('first_aired', show)
		meta['year'] = int(self.meta_map('year', show, default=0))
		meta['trailer_url'] = self.meta_map('trailer', show)
		meta['genre'] = self.meta_map('genres', show)
		meta['studio'] = self.meta_map('network', show)
		meta['status'] = self.meta_map('status', show)
		meta['cast'] = []
		meta['banner_url'] = self.meta_map(['images', 'thumb', 'full'], show)
		meta['cover_url'] = self.meta_map(['images', 'poster', 'full'], show)
		meta['backdrop_url'] = self.meta_map(['images', 'fanart', 'full'], show)
		meta['overlay'] = 6
		meta['playcount'] = 0
		if meta['imdb_id'] is None or meta['imdb_id']=='':
			imdb_id = self.resolve_imdb_id(meta['TVShowTitle'], meta['year'], 'series', meta['tmdb_id'], meta['trakt_id'])
			meta['imdb_id'] = imdb_id
		SQL = """INSERT OR REPLACE INTO tvshows (
				imdb_id,
				tmdb_id,
				tvdb_id,
				trakt_id,
				slug,
				title,
				year,
				TVShowTitle,
				duration,
				rating,
				plot,
				mpaa,
				cover_url,
				banner_url,
				backdrop_url,
				trailer_url,
				overlay,
				playcount
				) VALUES(?,?,?,?,? ,?,?,?,?,?, ?,?,?,?,?, ?,?,?)
				"""
				
		values = [meta[k] for k in ["imdb_id","tmdb_id","tvdb_id","trakt_id","slug","title","year","TVShowTitle","duration","rating","plot","mpaa","cover_url","banner_url","backdrop_url","trailer_url","overlay","playcount"]]
		DB.execute(SQL, values)
		DB.commit()
		return meta
		
	def process_movie(self, record):
		try:
			movie = record['movie']
		except:
			movie = record
			
		meta = {}
		meta['imdb_id'] = self.meta_map(['ids', 'imdb'], movie)
		meta['tmdb_id'] = self.meta_map(['ids', 'tmdb'], movie)
		meta['trakt_id'] = self.meta_map(['ids', 'trakt'], movie)
		meta['slug'] = self.meta_map(['ids', 'slug'], movie)
		meta['title'] = self.meta_map('title', movie)
		meta['year'] = int(self.meta_map('year', movie, default=0))
		meta['writer'] = ''
		meta['director'] = ''
		meta['tagline'] = self.meta_map('tagline', movie)
		meta['cast'] = []
		meta['rating'] = self.meta_map('rating', movie)
		meta['votes'] = self.meta_map('votes', movie)
		meta['duration'] = self.meta_map('runtime', movie)
		meta['plot'] = self.meta_map('overview', movie)
		meta['mpaa'] = self.meta_map('certification', movie)
		meta['premiered'] = self.meta_map('released', movie)
		meta['trailer_url'] = self.meta_map('trailer', movie)
		meta['genre'] = self.meta_map('genres', movie)
		meta['studio'] = ''
		meta['thumb_url'] = self.meta_map(['images', 'thumb', 'full'], movie)
		meta['cover_url'] = self.meta_map(['images', 'poster', 'full'], movie)
		meta['backdrop_url'] = self.meta_map(['images', 'fanart', 'full'], movie)
		meta['overlay'] = 6
		meta['playcount'] = 0
		if meta['imdb_id'] is None or meta['imdb_id'] =='None':
			imdb_id = self.resolve_imdb_id(meta['title'], meta['year'], 'movie', meta['tmdb_id'], meta['trakt_id'])
			meta['imdb_id'] = imdb_id
		SQL = """INSERT OR REPLACE INTO movies (
				imdb_id,
				tmdb_id,
				trakt_id,
				slug,
				title,
				year,
				tagline,
				duration,
				rating,
				votes,
				plot,
				mpaa,
				premiered,
				cover_url,
				thumb_url,
				backdrop_url,
				trailer_url,
				overlay,
				playcount
				) VALUES(?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?,?,?)
				"""
		values = [meta[k] for k in ["imdb_id","tmdb_id","trakt_id","slug", "title","year","tagline","duration","rating","votes","plot","mpaa","premiered","cover_url","thumb_url","backdrop_url","trailer_url","overlay","playcount"]]
		DB.execute(SQL, values)
		DB.commit()
		return meta
	
	def process_episode(self, record, watched=None, show=None):

		if 'show' in record.keys():
			show = record['show']
			episode = record['episode']
			meta = {}
			meta['imdb_id']= self.meta_map(['ids', 'imdb'], show) 				# show['ids']['imdb']
			meta['tvdb_id']= self.meta_map(['ids', 'tvdb'], show) 				# show['ids']['tvdb']
			meta['tmdb_id']= self.meta_map(['ids', 'tmdb'], show) 				# show['ids']['tmdb']
			meta['slug']= self.meta_map(['ids', 'slug'], show) 				# show['ids']['tmdb']
			meta['trakt_id']= self.meta_map(['ids', 'trakt'], episode) 			# episode['ids']['trakt']
			meta['year'] = int(self.meta_map('year', show, default=0)) 			# int(show['year'])
			meta['episode_id'] = ''
			meta['season']= int(self.meta_map('season', episode, default=0)) 	# int(episode['season'])
			meta['episode']= int(self.meta_map('number', episode, default=0)) 	# int(episode['number'])
			meta['title']= self.meta_map('title', episode) 						# episode['title']
			meta['showtitle'] = self.meta_map('title', show) 					# #show['title']
			meta['director'] = ''
			meta['writer'] = ''
			meta['plot'] = self.meta_map('overview', episode) 					# episode['overview']
			meta['rating'] = self.meta_map('rating', episode) 					# episode['rating']
			meta['premiered'] = self.meta_map('first_aired', episode) 			# episode['first_aired']
			meta['poster'] = self.meta_map(['images', 'poster', 'full'], show) 	# show['images']['poster']['full']
			meta['cover_url']= self.meta_map(['images', 'screenshot', 'full'], episode) 	# episode['images']['screenshot']['full']
			meta['trailer_url']=''
			meta['backdrop_url'] = self.meta_map(['images', 'fanart', 'full'], show) 	# show['images']['fanart']['full']
			meta['overlay'] = 6
			meta['playcount'] = 0
			if watched:
				for w in watched:
					if w['episode']['number'] == meta['episode']:
						meta['overlay'] = 7
						meta['playcount'] = 1
						break
			if meta['imdb_id'] is None:
				imdb_id = self.resolve_imdb_id(meta['showtitle'], meta['year'], 'series', meta['tmdb_id'], meta['trakt_id'])
				meta['imdb_id'] = imdb_id
			if meta['season'] != 0 and meta['episode'] != 0:
				SQL = """INSERT OR REPLACE INTO episodes (
					imdb_id,
					tmdb_id,
					tvdb_id,
					trakt_id,
					slug,
					title,
					showtitle,
					year,
					season,
					episode,
					rating,
					plot,
					premiered,
					cover_url,
					backdrop_url,
					poster,
					overlay,
					playcount
					) VALUES(?,?,?,?,? ,?,?,?,?,?, ?,?,?,?,?, ?,?,?)
					"""
				values = [meta[k] for k in ["imdb_id","tmdb_id","tvdb_id","trakt_id","slug","title","showtitle","year","season", "episode", "rating","plot","cover_url","backdrop_url","trailer_url","poster","overlay","playcount"]]
				DB.execute(SQL, values)
				DB.commit()
			return meta
		else:
			meta = {}
			episode = record
			meta['premiered'] = self.meta_map('first_aired', episode)
			tmp = re.match('^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})\.000Z', meta['premiered'])
			if tmp:
				year = tmp.group(1)
				aired = datetime(int(tmp.group(1)), int(tmp.group(2)),int(tmp.group(3)),int(tmp.group(4)),int(tmp.group(5)),int(tmp.group(6)))
				aired = time.mktime(aired.timetuple())
				now = time.mktime(datetime.now().timetuple())
			else:
				return False
			if aired < now:
				meta['imdb_id']= self.meta_map(['ids', 'imdb'], show) 			# episode['ids']['imdb']
				meta['tvdb_id']= self.meta_map(['ids', 'tvdb'], show) 			# episode['ids']['tvdb']
				meta['tmdb_id']= self.meta_map(['ids', 'tmdb'], show) 			# episode['ids']['tmdb']
				meta['trakt_id']= self.meta_map(['ids', 'trakt'], show) 			# episode['ids']['trakt']
				meta['slug']= self.meta_map(['ids', 'slug'], show) 			# episode['ids']['trakt']
				meta['year'] = year
				meta['episode_id'] = ''
				meta['season']= int(self.meta_map('season', episode, default=0))		# int(episode['season'])
				meta['episode']= int(self.meta_map('number', episode, default=0))	#int(episode['number'])
				meta['title']= self.meta_map('title', episode)						# episode['title']
				meta['showtitle'] = self.meta_map('title', show) 
				meta['director'] = ''
				meta['writer'] = ''
				meta['plot'] = self.meta_map('overview', episode) 					#episode['overview']
				meta['rating'] = self.meta_map('rating', episode) 					#episode['rating']
				meta['premiered'] = self.meta_map('first_aired', episode) 			#episode['first_aired']
				meta['poster'] = ''
				meta['cover_url']= self.meta_map(['images', 'screenshot', 'full'], episode)
				meta['trailer_url']=''
				meta['backdrop_url'] = ''
				meta['overlay'] = 6
				meta['playcount'] = 0
				if watched:
					for w in watched:
						if w['episode']['number'] == meta['episode']:
							meta['overlay'] = 7
							meta['playcount'] = 1
							break
				SQL = """INSERT OR REPLACE INTO episodes (
				imdb_id,
				tmdb_id,
				tvdb_id,
				trakt_id,
				slug,
				title,
				showtitle,
				year,
				season,
				episode,
				rating,
				plot,
				premiered,
				cover_url,
				backdrop_url,
				poster,
				overlay,
				playcount
				) VALUES(?,?,?,?,? ,?,?,?,?,?, ?,?,?,?,?, ?,?,?)
				"""
				values = [meta[k] for k in ["imdb_id","tmdb_id","tvdb_id","trakt_id","slug","title","showtitle","year","season", "episode", "rating","plot","cover_url","backdrop_url","trailer_url","poster","overlay","playcount"]]
				DB.execute(SQL, values)
				DB.commit()
				return meta
			return False

	def raise_error(self, code, title, message):
		if code in [500, 502, 503, 504, 520, 521, 522, 524]:
			message = "Temporary " + message
		from dudehere.routines.plugin import Plugin
		image = vfs.join(ARTWORK, 'trakt_error.png')
		if vfs.exists(image) is False:
			image = vfs.join(ROOT_PATH, 'icon.png')
		Plugin().error_message(title, message, image=image)

	
	def _cache_result(self, result, url, media):
		#DB.connect()
		hash_id = hashlib.md5(url).hexdigest()
		DB.execute("DELETE FROM cache WHERE cache.id in (select id FROM stale_cache)")
		SQL = "INSERT INTO cache(hash_id, url, media, results) VALUES(?,?,?,?)"
		DB.execute(SQL, [hash_id, url, media, base64.b64encode(result)])
		DB.commit()
		#DB.disconnect()
		
	def _clear_watchlist_cache(self):
		#DB.connect()
		DB.execute("DELETE FROM cache WHERE media='watchlist'")
		DB.commit()
		#DB.disconnect()
	
	def _get_cached_result(self, url):
		result = False
		#DB.connect()
		DB.execute("DELETE FROM cache WHERE cache.id in (select id FROM stale_cache)")
		hash_id = hashlib.md5(url).hexdigest()
		cache = DB.query("SELECT results FROM cache WHERE hash_id=?", [hash_id])
		if cache:
			result = base64.b64decode(cache[0])
		DB.commit()
		#DB.disconnect()
		return result
	
	def _authorize(self, pin=None):
		uri = '/oauth/token'
		data = {'client_id': CLIENT_ID, 'client_secret': SECRET_ID, 'redirect_uri': REDIRECT_URI}
		if pin:
			data['code'] = pin
			data['grant_type'] = 'authorization_code'
		else:
			refresh_token = ADDON.get_setting('trakt_refresh_token')
			if refresh_token:
				data['refresh_token'] = refresh_token
				data['grant_type'] = 'refresh_token'
			else:
				ADDON.set_setting('trakt_oauth_token', '')
				ADDON.set_setting('trakt_refresh_token', '')
				ADDON.set_setting('trakt_authorized', 'false')
				ADDON.set_setting('trakt_account', '')
				ADDON.log("Authentication Error, Please you must authorize with Tratk.")
				return False
		if self.token is None: self.token = False
		response = self._call(uri, data, auth=False)
		if response is False or response is None or response == '':
			return False
		if 'access_token' in response.keys() and 'refresh_token' in response.keys():
			ADDON.set_setting('trakt_oauth_token', response['access_token'])
			ADDON.set_setting('trakt_refresh_token', response['refresh_token'])
			ADDON.set_setting('trakt_authorized', "true")
			self.token = response['access_token']
#			settings = self.get_settings()
#			if settings:
#				ADDON.set_setting('trakt_account', settings['user']['username'])
			return True
	
	def _call(self, uri, data=None, params=None, auth=False, cache=False, timeout=None):

		if timeout is not None: self.timetout = timeout
		json_data = json.dumps(data) if data else None
		headers = {'Content-Type': 'application/json', 'trakt-api-key': CLIENT_ID, 'trakt-api-version': 2}
		if auth: 
			self._authorize()
			if self.token is None:
				raise TraktError('Trakt Authorization Required: 400')
			headers.update({'Authorization': 'Bearer %s' % (self.token)})
		url = '%s%s' % (BASE_URL, uri)
		if params and not uri.endswith('/token'):
			params['limit'] = self.limit
		else:
			params = {'limit': self.limit}
		url = url + '?' + urllib.urlencode(params)
		
		if cache and not uri.endswith('/token'):
			result = self._get_cached_result(url)
			if result:
				response = json.loads(result)
				ADDON.log("Returning cached results")
				return response
		try:
			request = urllib2.Request(url, data=json_data, headers=headers)
			f = urllib2.urlopen(request, timeout=self.timeout)
			result = f.read()
			response = json.loads(result)
		except HTTPError as e:
			ADDON.log(url, LOG_LEVEL.VERBOSE)
			if not uri.endswith('/token'):
				self.raise_error(e.code, "Trakt error", 'HTTP ERROR: %s' % e)
			return False
		except URLError as e:
			ADDON.log(url, LOG_LEVEL.VERBOSE)
			if not uri.endswith('/token'):
				self.raise_error(-1, "Trakt error", 'URL ERROR: %s' % e)
			return False
		except socket.timeout as e:
			self.raise_error(-1, "Trakt error", 'Socket Timeout: %s' % e)
			return False
		if cache:
			self._cache_result(result, url, cache)
		return response
	

	
	def _delete(self, uri, data=None, params=None, auth=True):
		json_data = json.dumps(data) if data else None
		url = '%s%s' % (BASE_URL, uri)
		opener = urllib2.build_opener(urllib2.HTTPHandler)
		headers = {'Content-Type': 'application/json', 'trakt-api-key': CLIENT_ID, 'trakt-api-version': 2}
		if auth: headers.update({'Authorization': 'Bearer %s' % (self.token)})
		try:
			request = urllib2.Request(url, data=json_data, headers=headers)
			request.get_method = lambda: 'DELETE'
			response = opener.open(request)
		except HTTPError as e:
			ADDON.log(url, LOG_LEVEL.VERBOSE)
			if not uri.endswith('/token'):
				self.raise_error(e.code, "Trakt error", 'HTTP ERROR: %s' % e)
			return False
		except URLError as e:
			ADDON.log(url, LOG_LEVEL.VERBOSE)
			if not uri.endswith('/token'):
				self.raise_error(e.code, "Trakt error", 'HTTP ERROR: %s' % e)
			return False
		except socket.timeout as e:
			self.raise_error(-1, "Trakt error", 'Socket Timeout: %s' % e)
			return False
		else:
			return response
		