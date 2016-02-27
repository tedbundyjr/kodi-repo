#!/usr/bin/python
# -*- coding: utf-8 -*-
PYTHONIOENCODING="UTF-8"

'''*
	Copyright (C) 2015 DudeHere

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
*'''

import sys
import os
import re
import xbmcaddon
from dudehere.routines import *
from resources.lib.i18n_strings import STRINGS as STRINGS_MAP
from dudehere.routines.i18nlib import i18n, LANGUAGE_PATH
from dudehere.routines.vfs import VFSClass
from dudehere.routines.plugin import Plugin, TextBox, ContextMenu, VIEWS
from resources.lib.constants import *
plugin =  Plugin()
vfs = VFSClass()
STRINGS = STRINGS_MAP()

def validate_advanced():
	return ADDON.get_setting('advanced_mode_1') == 'true'

def validate_transmogrifier():
	return False
	try:
		return xbmcaddon.Addon('service.transmogrifier').getSetting('enable_transmogrifier') == "true"
	except:
		return False

def validate_trakt():
	return ADDON.get_setting('trakt_authorized') == "true"

plugin.replace_context_menu_by_default = True
plugin.set_default_context_menu([(30034, {'mode': 'manage_transmogrifier'}, True, validate_transmogrifier), (30033, {"mode": "set_language"}, True), (30032, {"mode": "alluc_settings", "addon_id": ADDON_ID}, True)])

IGNORE_UNIQUE_ERRORS = True
if DB_TYPE == 'mysql':
	from dudehere.routines.database import MySQLDatabase as DatabaseAPI
else:
	from dudehere.routines.database import SQLiteDatabase as DatabaseAPI
	
if not vfs.exists(DATA_PATH): vfs.mkdir(DATA_PATH)

class MyDatabaseAPI(DatabaseAPI):
	def _initialize(self):
		schema_file = vfs.join(ROOT_PATH, 'resources/database/schema.%s.sql' % self.db_type)
		if self.run_script(schema_file, commit=False):
			self.execute('DELETE FROM version_alluc WHERE 1')
			self.execute('INSERT INTO version_alluc(db_version) VALUES(?)', [self.db_version])
			self.commit()
		
	def do_init(self):
		do_init = True
		try:
			test = self.query("SELECT 1 FROM version_alluc WHERE db_version >= ?", [self.db_version])
			if test:
				do_init = False
		except:
			do_init = True
		return do_init
DB_VERSION = 4
if DB_TYPE == 'mysql':
	DB=MyDatabaseAPI(DB_ADDRESS, DB_NAME, DB_USER, DB_PASS, DB_PORT, version=DB_VERSION, connect=ADDON.get_setting('database_mysql_init')=="false")
else:
	DB=MyDatabaseAPI(DB_FILE, version=DB_VERSION, connect=ADDON.get_setting('database_sqlite_init')=="false")


def update_run():
	if plugin.check_version(ADDON.get_setting('version'), '0.4.19'):
		ADDON.set_setting('database_sqlite_init', "false")
		ADDON.set_setting('database_sqlite_init.cache', "false")
		ADDON.set_setting('database_mysql_init', "false")
		ADDON.set_setting('database_mysql_init.cache', "false")
		ADDON.set_setting('database_mysql_version', "1")
		ADDON.set_setting('database_mysql_version.cache', "1")
		first_run(True)
plugin.update_run = update_run

def first_run(upgrade=False):
	vfs = VFSClass()
	from dudehere.routines.window import Window
	from dudehere.routines.manager import Manager

	class FirstPage(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title)
			self.overide_actions = {"next_button": self.erase_and_next}
			self.overide_strings = {"next_button": i18n(33011)}
		
		def erase_and_next(self):
			plugin.initialize_settings(upgrade)
			WM.next_page()
			
		def set_info_controls(self):
			def cancel():
				self.close()
				plugin.exit()
			content = i18n(33000)
			self.add_label(self.create_label(content), 0, 0, columnspan=4, rowspan=5, pad_x=15, pad_y=10)
			
			self.create_button("cancel", i18n(33013))
			self.add_object("cancel", 5, 0)
			self.set_object_event('action', 'cancel', cancel)
			
	class SecondPage(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title, width=800, height=450, columns=4, rows=6)
			self.overide_strings = {"next_button": i18n(33014), "previous_button": i18n(33012)}
			
		def set_info_controls(self):	
			path = vfs.join(LANGUAGE_PATH, 'disclosure.txt', True)
			content  = vfs.read_file(path)
			self.add_label(self.create_label(content), 0, 0, columnspan=4, rowspan=5, pad_x=15, pad_y=10)
			
			self.create_button("decline", i18n(33015))
			self.add_object("decline", 5, 2)
			def decline():
				self.close()
				plugin.exit()
			self.set_object_event("action", "decline", decline)
			
	class ThirdPage(Window):	
		def set_info_controls(self):
			self.overide_strings = {"next_button": i18n(33011), "previous_button": i18n(33012)}
			content = i18n(33001)
			self.add_label(self.create_label(content), 0, 0, columnspan=4, rowspan=3, pad_x=15, pad_y=10)
			
			self.create_list('usage')
			self.add_object('usage', 2,0,3,4)
			self.add_list_items('usage', [i18n(30054), i18n(30055)], 0, allow_multiple=False, allow_toggle=False)
			
	class FourthPage(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title)
			self.overide_strings = {"next_button": i18n(33011), "previous_button": i18n(33012)}
			
		def set_info_controls(self):
			from resources.lib.language import LanguageClass
			lang = LanguageClass()
			def set_lang():
				obj = self.getFocus()
				for index in xrange(self.get_object('language').size()):
					selected = self.get_object('language').getListItem(index).getLabel2()
					if selected:
						self.get_object('language').getListItem(index).setLabel(selected)
						self.get_object('language').getListItem(index).setLabel2('')
				#
				language = obj.getSelectedItem().getLabel()
				obj.getSelectedItem().setLabel('[B][COLOR %s]%s[/COLOR][/B]' % (ENABLED_COLOR, language))
				obj.getSelectedItem().setLabel2(language)
				code = lang.get_code_by_lang(language)
				if code:
					ADDON.set_setting('alluc_api_language', code)
				else:
					ADDON.set_setting('alluc_api_language', '')
				
			content = i18n(33002)
			self.add_label(self.create_label(content), 0, 0, columnspan=4, rowspan=3, pad_x=15, pad_y=10)
			self.create_list('language')
			self.add_object('language', 1,0,5,4)
			self.add_list_items('language', lang.get_languages(), selectable=False, call_back=set_lang)
			
			for index in xrange(self.get_object('language').size()):
				language = self.get_object('language').getListItem(index).getLabel()
				code = lang.get_code_by_lang(language)
				if code:
					icon = vfs.join(ARTWORK, 'flags/%s.png' % code)
					self.get_object('language').getListItem(index).setIconImage(icon)
				else:
					self.get_object('language').getListItem(index).setLabel('[B][COLOR %s]%s[/COLOR][/B]' % (ENABLED_COLOR, language))
					self.get_object('language').getListItem(index).setLabel2(language)

				
	class FifthPage(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title)
			self.overide_strings = {"next_button": i18n(33011), "previous_button": i18n(33012)}
			
			def next_action():
				valid = True
				from dudehere.routines.scrapers import CommonScraper
				Scraper = CommonScraper(load=['alluc_api'])
				username = self.get_value('username')
				password = self.get_value('password')
				valid = Scraper.get_scraper_by_index(0).check_authentication(username, password)
				if not valid:
					plugin.dialog_ok(i18n(33006), i18n(33007))

				if valid:
					self.get_object('verified').setVisible(True)
					ADDON.set_setting('alluc_api_username', username)
					ADDON.set_setting('alluc_api_password', password)
					
					WM.next_page()
			
			self.overide_actions = {"next_button": next_action}
				
		def set_info_controls(self):
					
			self.add_label(self.create_label(i18n(33003)), 0, 0, columnspan=4, rowspan=2, pad_x=15, pad_y=10)
			
			self.add_label(self.create_label(i18n(33004), alignment=1), 2, 0, pad_x=15)
			
			self.create_input('username')
			self.add_object('username', 2, 1, columnspan=2)
			self.set_value('username', ADDON.get_setting('alluc_api_username'))
			
			self.add_label(self.create_label(i18n(33005), alignment=1), 3, 0, pad_x=15)
			
			self.create_input('password', isPassword=True)
			self.add_object('password', 3, 1, columnspan=2)
			self.set_value('password', ADDON.get_setting('alluc_api_password'))
			
			self.create_image('verified', ARTWORK + 'checked.png', aspectRatio=2)
			self.add_object('verified', 2, 3)
			self.get_object('verified').setVisible(False)

			
	class SixthPage(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title)
			self.overide_strings = {"previous_button": i18n(33012)}
			
		def authorize(self):
			pin = self.get_value('pin')
			from dudehere.routines.trakt import TraktAPI
			trakt = TraktAPI()
			response = trakt.authorize(pin)
			if response:
				settings = trakt.get_settings()
				if settings:
					ADDON.set_setting('trakt_account', settings['user']['username'])
				self.get_object('authorized').setVisible(True)
				plugin.notify(i18n(33018), i18n(33019), image=ARTWORK + "trakt.png")
			else:
				ADDON.set_setting('trakt_account', '')
				plugin.notify(i18n(33018), i18n(33020), image=ARTWORK + "trakt.png")

		def set_info_controls(self):
			self.create_image('trakt', ARTWORK + 'trakt.png', aspectRatio=1)
			self.add_object('trakt', 0, 0, columnspan=3, rowspan=3)
			
			content = i18n(33008)
			self.add_label(self.create_label(content), 0, 0, columnspan=3, rowspan=3, pad_x=15, pad_y=10)
			
			content = i18n(33009) % ADDON.get_setting('trakt_pin_url')
			self.add_label(self.create_label(content), 3, 0, columnspan=3, rowspan=2, pad_x=15, pad_y=10)
			
			self.create_input('pin', _alignment=2)
			self.add_object('pin', 4, 0, columnspan=3)
			
			self.create_image('qr_code', ARTWORK + 'qr_code.png', aspectRatio=2)
			self.add_object('qr_code', 0, 3, columnspan=1, rowspan=2)
			
			self.create_image('authorized', ARTWORK + 'checked.png', aspectRatio=2)
			self.add_object('authorized', 2, 3)
			self.get_object('authorized').setVisible(False)
			
			self.create_button('authorize',  i18n(33017))
			self.add_object('authorize', 4, 3)	
			self.set_object_event('action', "authorize", self.authorize)
			
			self.create_button('finalize', i18n(33016))
			self.add_object('finalize', 5, 3)
			
	class ConfirmationPage(Window):	
		def set_info_controls(self):
			bg = vfs.join(ARTWORK, 'confirmation.jpg')
			self.create_image('background', bg, aspectRatio=0)
			self.add_object('background', 0, 0, rowspan=6, columnspan=3, pad_x=0, pad_y=0)
			self.add_label(self.create_label(i18n(33010), alignment=2, font="font14"), 0, 0, columnspan=3, rowspan=5, pad_x=15, pad_y=15)

	WM = Manager()
	WM.add_page(FirstPage(i18n(33021) % VERSION))
	WM.add_page(SecondPage(i18n(33022)  % VERSION))
	WM.add_page(ThirdPage(i18n(33023) % VERSION))
	WM.add_page(FourthPage(i18n(33024) % VERSION))
	WM.add_page(FifthPage(i18n(33025) % VERSION))
	WM.add_page(SixthPage(i18n(33026) % VERSION))
	WM.add_confirmation(ConfirmationPage(i18n(33027)))
	WM.build()
	def complete_setup():
		WM.show_confirmation()
		ADDON.set_setting('setup_run', 'true')
		ADDON.set_setting('version', VERSION)
		usage_mode = WM.get_value(2, 'usage')
		if usage_mode[1]:
			for i in range(1,8):
				ADDON.set_setting('advanced_mode_%s' %  i, 'true')
	WM.set_object_event(5, "action", "finalize", complete_setup)
	WM.set_focus(0, 'next_button')
	WM.set_object_event(0, 'left', 'next_button', 'cancel')
	WM.set_object_event(0, 'right', 'cancel', 'next_button')
	WM.set_focus(1, 'decline')
	WM.set_object_event(1, 'left', 'next_button', 'decline')
	WM.set_object_event(1, 'left', 'decline', 'previous_button')
	WM.set_object_event(1, 'right', 'decline', 'next_button')
	WM.set_object_event(1, 'right', 'previous_button', 'decline')
	WM.set_focus(2, 'next_button')
	WM.set_object_event(2, 'left', 'next_button', 'previous_button')
	WM.set_object_event(2, 'right', 'previous_button', 'next_button')
	WM.set_object_event(2, 'up', 'next_button', 'usage')
	WM.set_object_event(2, 'up', 'previous_button', 'usage')
	WM.set_object_event(2, 'down', 'usage', 'next_button')
	WM.set_object_event(2, 'right', 'usage', 'next_button')
	WM.set_focus(3, 'next_button')
	WM.set_object_event(3, 'left', 'next_button', 'previous_button')
	WM.set_object_event(3, 'right', 'previous_button', 'next_button')
	WM.set_object_event(3, 'up', 'next_button', 'language')
	WM.set_object_event(3, 'up', 'previous_button', 'language')
	WM.set_object_event(3, 'down', 'language', 'next_button')
	WM.set_object_event(3, 'right', 'language', 'next_button')
	WM.set_focus(4, 'username')
	WM.set_object_event(4, 'left', 'next_button', 'previous_button')
	WM.set_object_event(4, 'right', 'previous_button', 'next_button')
	WM.set_object_event(4, 'up', 'next_button', 'password')
	WM.set_object_event(4, 'up', 'previous_button', 'password')
	WM.set_object_event(4, 'up', 'password', 'username')
	WM.set_object_event(4, 'down', 'username', 'password')
	WM.set_object_event(4, 'down', 'password', 'next_button')
	
	WM.set_focus(5, 'finalize')
	WM.set_object_event(5, 'left', 'finalize', 'previous_button')
	WM.set_object_event(5, 'right', 'previous_button', 'finalize')
	WM.set_object_event(5, 'up', 'finalize', 'pin')
	WM.set_object_event(5, 'up', 'previous_button', 'pin')
	WM.set_object_event(5, 'right', 'pin', 'authorize')
	WM.set_object_event(5, 'left', 'authorize', 'pin')
	WM.set_object_event(5, 'down', 'pin', 'finalize')
	WM.set_object_event(5, 'down', 'authorize', 'finalize')
	WM.show()
plugin.first_run = first_run	


def main_menu():
	plugin.add_menu_item({'mode': 'tv_menu'}, {'title': STRINGS.map('tv_menu')}, image=ARTWORK + 'tvshows.jpg')
	plugin.add_menu_item({'mode': 'movie_menu'}, {'title': STRINGS.map('movie_menu')}, image=ARTWORK + 'movies.jpg')
	plugin.add_menu_item({'mode': 'set_language'}, {'title': STRINGS.map('set_language')}, image=ARTWORK + 'languages.jpg')
	plugin.add_video_item({'mode': 'quick_search'}, {'title': STRINGS.map('quick_search')}, image=ARTWORK + 'search_quick.jpg')
	plugin.add_menu_item({'mode': 'settings_menu'}, {'title': STRINGS.map('settings_menu')}, image=ARTWORK + 'settings_alluc.jpg')
	plugin.add_menu_item({'mode': 'transmogrified_menu'}, {'title': STRINGS.map('transmogrified')}, image=ARTWORK + 'transmogrified.jpg', visible=validate_transmogrifier)
	plugin.add_menu_item({'mode': 'update_all'}, {'title': STRINGS.map('update_now')}, image=ARTWORK + 'update_now.jpg', visible=validate_advanced)
	plugin.add_menu_item({'mode': 'authorize_trakt'}, {'title': STRINGS.map('authorize_trakt')}, image=ARTWORK + 'trakt.jpg', visible=validate_trakt()==False)
	plugin.add_menu_item({'mode': 'show_help'}, {'title': STRINGS.map('show_help')}, image=ARTWORK + 'help.jpg')
	plugin.eod(clear_search=True)
plugin.register('main', main_menu)

def tv_menu():
	plugin.add_menu_item({'mode': 'tv_favorites'}, {'title': STRINGS.map('my_favorites')}, image=ARTWORK + "favorites.jpg", visible=validate_trakt()==False)
	plugin.add_menu_item({'mode': 'tv_calendar'}, {'title': STRINGS.map('tv_calendar')}, image=ARTWORK + 'calendar.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'tv_watchlist'}, {'title': STRINGS.map('watchlist')}, image=ARTWORK + 'watchlist.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'tv_custom_lists'}, {'title': STRINGS.map('custom_lists')}, image=ARTWORK + 'custom_list.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'tv_recommended'}, {'title': STRINGS.map('tv_recommended')}, image=ARTWORK + 'recommended.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'tv_popular'}, {'title': STRINGS.map('tv_popular')}, image=ARTWORK + 'popular.jpg')
	plugin.add_menu_item({'mode': 'tv_trending'}, {'title': STRINGS.map('tv_trending')}, image=ARTWORK + 'trending.jpg')
	plugin.add_menu_item({'mode': 'tv_search'}, {'title': STRINGS.map('search')}, image=ARTWORK + 'search.jpg')
	plugin.eod(clear_search=True)
plugin.register('tv_menu', tv_menu)

def movie_menu():
	plugin.add_menu_item({'mode': 'movie_favorites'}, {'title': STRINGS.map('my_favorites')}, image=ARTWORK + "favorites.jpg", visible=validate_trakt()==False)
	plugin.add_menu_item({'mode': 'movie_watchlist'}, {'title': STRINGS.map('watchlist')}, image=ARTWORK + 'watchlist.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'movie_custom_lists'}, {'title': STRINGS.map('custom_lists')}, image=ARTWORK + 'custom_list.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'movie_recommended'}, {'title': STRINGS.map('movie_recommended')}, image=ARTWORK + 'recommended.jpg', visible=validate_trakt)
	plugin.add_menu_item({'mode': 'movie_popular'}, {'title': STRINGS.map('movie_popular')}, image=ARTWORK + 'popular.jpg')
	plugin.add_menu_item({'mode': 'movie_trending'}, {'title': STRINGS.map('movie_trending')}, image=ARTWORK + 'trending.jpg')
	plugin.add_menu_item({'mode': 'movie_search'}, {'title': STRINGS.map('search')}, image=ARTWORK + 'search.jpg')
	plugin.add_menu_item({'mode': 'movie_advanced_search'}, {'title': STRINGS.map('advanced_search')}, image=ARTWORK + 'advanced_search.jpg')
	plugin.eod(clear_search=True)
plugin.register('movie_menu', movie_menu)
	
def settings_menu():
	plugin.add_menu_item({'mode': 'authorize_trakt'}, {'title': STRINGS.map('authorize_trakt')}, image=ARTWORK + 'trakt.jpg')
	plugin.add_menu_item({'mode': 'add_source_folders'}, {'title': STRINGS.map('add_source_folders')}, image=ARTWORK + 'add_source_folders.jpg', visible=validate_advanced)
	plugin.add_menu_item({'mode': 'manage_subscriptions'}, {'title': STRINGS.map('manage_subscriptions')}, image=ARTWORK + 'subscriptions.jpg', visible=validate_advanced)
	plugin.add_menu_item({'mode': 'manage_hostlist'}, {'title': STRINGS.map('manage_hostlist')}, image=ARTWORK + 'hoster_list.jpg', visible=False)
	plugin.add_menu_item({'mode': 'advanced_mode'}, {'title': STRINGS.map('enable_basic_mode')}, image=ARTWORK + "advanced_mode.jpg", visible=validate_advanced())
	plugin.add_menu_item({'mode': 'advanced_mode'}, {'title': STRINGS.map('enable_advanced_mode')}, image=ARTWORK + "basic_mode.jpg", visible=validate_advanced() is False)
	plugin.add_menu_item({'mode': 'alluc_settings', 'addon_id': 'plugin.video.alluc.api'}, {'title': STRINGS.map('alluc_settings')}, image=ARTWORK + 'settings_alluc.jpg')
	plugin.add_menu_item({'mode': 'transmogrifier_menu'}, {'title': STRINGS.map('transmogrifier_settings')}, image=ARTWORK + 'transmogrified.jpg', visible=validate_transmogrifier)
	plugin.add_menu_item({'mode': 'urlresolver_settings', 'addon_id': 'script.module.urlresolver'}, {'title': STRINGS.map('urlresolver_settings')}, image=ARTWORK + 'urlresolver.jpg')
	plugin.add_menu_item({'mode': 'reset_alluc'}, {'title': STRINGS.map('reset_alluc')}, image=ARTWORK + 'reset.jpg')
	plugin.eod(clear_search=True)
plugin.register('settings_menu', settings_menu)
	
def transmogrifier_menu():
	plugin.add_menu_item({'mode': 'tv_transmogrified'}, {'title': STRINGS.map('tv_transmogrified')}, image=ARTWORK + 'add_source_folders.jpg')
	plugin.add_menu_item({'mode': 'movie_transmogrified'}, {'title': STRINGS.map('movie_transmogrified')}, image=ARTWORK + 'subscriptions.jpg')
	plugin.add_menu_item({'mode': 'transmogrifier_queue'}, {'title': STRINGS.map('transmogrifier_queue')}, image=ARTWORK + 'hoster_list.jpg')
	plugin.eod(clear_search=True)
plugin.register('transmogrifier_menu', transmogrifier_menu)

def tv_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	if plugin.mode == 		'tv_watchlist' or validate_trakt() is False:
		watchlist = []
	else:
		watchlist = trakt.get_watchlist_tvshows(simple=True)
	if plugin.mode == 		'tv_favorites':
		results = get_tv_favorites()
	elif plugin.mode == 		'tv_watchlist':
		results = trakt.get_watchlist_tvshows()
		results = sorted(results, key=lambda x: x['show']['title'])
	elif plugin.mode == 	'tv_trending':
		results = trakt.get_trending_tvshows()
	elif plugin.mode == 	'tv_popular':
		results = trakt.get_popular_tvshows()
	elif plugin.mode ==		'tv_recommended':
		results = trakt.get_recommended_tvshows()
	elif plugin.mode ==		'tv_custom_list':
		results = trakt.get_custom_list(plugin.args['slug'], 'tvshows')	
	elif plugin.mode ==		'tv_search':
		query = plugin.get_property('search.query.refesh')
		if query:
			plugin.clear_property('search.query')
			plugin.clear_property('search.query.refesh')
		else:
			query = plugin.dialog_input(i18n(30056))
			
		if query is None: 
			plugin.clear_property("search.query")
			return
		plugin.set_property('search.query', query)
		results = trakt.search(query, 'show')
	elif plugin.mode == 	'tv_similar':
		imdb_id = trakt.query_id('tmdb', plugin.args['tmdb_id']) if plugin.args['imdb_id'] == 'None' else plugin.args['imdb_id']
		results = trakt.get_similar_tvshows(imdb_id)
	if not results:
		return
	for record in results:
		if plugin.mode != 'tv_favorites':
			record = trakt.process_record(record, media='tvshow')
		else:
			record['cast'] = []
		menu = ContextMenu()
		menu.add(30035, {"mode": "tv_similar", "imdb_id": record['imdb_id']})
		menu.add(30036, {"mode": "subscribe", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "title": record['title']}, script=True, visible=validate_advanced)
		if plugin.mode == 	'tv_watchlist':
			menu.add(30037, {"mode": "tv_delete_from_watchlist", "imdb_id": record['imdb_id'], "name": record['title']}, script=True, visible=validate_trakt)
		else:
			if record['imdb_id'] in watchlist: 
				record['title'] = '[COLOR %s]%s[/COLOR]' % (WATCHLIST_COLOR, record['title'])
				menu.add(30037, {"mode": "tv_delete_from_watchlist", "imdb_id": record['imdb_id'], "name": record['title']}, script=True, visible=validate_trakt)
			else:
				menu.add(30038, {"mode": "tv_add_to_watchlist", "imdb_id": record['imdb_id']}, script=True, visible=validate_trakt)
				
		if plugin.mode ==	'tv_custom_list':
			menu.add(30039, {"mode": "delete_from_custom_list", "media": "tvshow", "imdb_id": record['imdb_id'], "slug": plugin.args['slug'], "name": record['title']}, script=True, visible=validate_trakt)
		else:
			menu.add(30040, {"mode": "add_to_custom_list", "media": "tvshow", "imdb_id": record['imdb_id']}, script=True, visible=validate_trakt)	
		if plugin.mode ==	'tv_favorites':
			menu.add('Delete Favorite', {"mode": "delete_from_favorites", "media": "tvshow", "title": record['title'], "id": record['id']}, script=True, visible=validate_trakt()==False)
		else:
			menu.add('Save as Favorite', {"mode": "add_to_favorites", "media": "tvshow",  "record": record}, script=True, visible=validate_trakt()==False)
		
		plugin.add_menu_item({'mode': 'season_list', "imdb_id": record['imdb_id'], "title": record['title'], "year": record['year'], "fanart": record['backdrop_url']}, record, menu=menu, replace_menu=True, image=record['cover_url'], fanart=record['backdrop_url'])
	plugin.eod(VIEWS.TV_DEFAULT, 'tvshows')	
plugin.register(['tv_watchlist', 'tv_trending', 'tv_popular', 'tv_recommended', 'tv_custom_list', 'tv_search', 'tv_similar', 'tv_favorites'], tv_list)

def season_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	imdb_id = trakt.query_id('tmdb', plugin.args['tmdb_id']) if 'tmdb_id' in plugin.args.keys() else plugin.args['imdb_id']	
	results = trakt.get_show_seasons(imdb_id)
	for record in results:
		if record['number'] > 0:
			menu = ContextMenu()
			season_id = record['ids']['trakt']
			image = record['images']['poster']['full']
			fanart = plugin.args['fanart']
			season = record['number']
			record = {"title": i18n(30057) % season}
			menu.add(i18n(30058), {"mode": "set_watched", "media": "season", "id": season, "imdb_id": imdb_id}, visible=validate_trakt)
			plugin.add_menu_item({'mode': 'episode_list', "imdb_id": imdb_id, "season": season, "season_id": season_id, "fanart": fanart}, record, menu=menu, image=image, fanart=fanart)
	plugin.eod(VIEWS.SEASON_DEFAULT, "tvshows")
plugin.register('season_list', season_list)
	
def episode_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	show = trakt.get_show_info(plugin.args['imdb_id'])
	results = trakt.get_show_episodes(plugin.args['imdb_id'], plugin.args['season'])
	if validate_trakt():
		watched = trakt.get_watched_episodes(plugin.args['season_id'])
	else:
		watched = None
	for record in results:
		record = trakt.process_record(record, media='episode', watched=watched)
		if record is False: continue
		if record['episode'] == 0: continue
		menu = ContextMenu()
		record['showtitle'] = show['title']
		record['year'] = show['year']
		record['title'] = "%s. %s" % (record['episode'], record['title'])
		record['imdb_id'] = plugin.args['imdb_id']
		if record['playcount'] == 0:
			menu.add(30041, {"mode": "set_watched", "media": "episode", "id": record['trakt_id'], "imdb_id": record['imdb_id']})
		else:
			if ADDON.get_setting('hide_watched_episodes') == "true" : continue
			record['overlay'] = 7
			menu.add(30042, {"mode": "set_unwatched", "media": "episode", "id": record['trakt_id']})
		plugin.add_video_item({'mode': 'play_episode', "display": record['title'], "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "year": record['year'], "showtitle": record['showtitle'], "season": record['season'], "episode": record['episode']}, record, menu=menu, image=record['cover_url'], fanart=plugin.args['fanart'])
	plugin.eod(VIEWS.EPISODE_DEFAULT, 'tvshows')
plugin.register('episode_list', episode_list)	

def tv_calendar():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()	
	results = trakt.get_calendar_shows()
	if validate_trakt():
		watched = trakt.get_watched_history('shows')
	else:
		watched = []
	count = len(results)
	for record in results:
		
		record = trakt.process_record(record, media='episode')
		if record['season'] == 0 or record['episode']== 0: continue
		if validate_trakt():
			if record['imdb_id'] in watched.keys():
				if record['season'] in watched[record['imdb_id']]:
					record['playcount'] = 1 if record['episode'] in watched[record['imdb_id']][record['season']] else 0
					if ADDON.get_setting('hide_watched_episodes') == "true" and record['playcount'] == 1: continue
		menu = ContextMenu()
		if record['playcount'] == 0:
			menu.add(30041, {"mode": "set_watched", "media": "episode", "id": record['trakt_id'], "imdb_id": record['imdb_id']})
		else:
			record['overlay'] = 7
			menu.add(30042, {"mode": "set_unwatched", "media": "episode", "id": record['trakt_id']})
		menu.add(30035, {"mode": "tv_similar", "imdb_id": record['imdb_id']})
		menu.add(30044, {"mode": "season_list", "imdb_id": record['imdb_id'], "fanart": record['backdrop_url']})
		record['title'] = "%sx%s. %s - %s" % (record['season'], record['episode'], record['showtitle'], record['title'])
		query = {'mode': 'tv_transmogrify', "display": record['title'], "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "year": record['year'], "showtitle": record['showtitle'], "season": record['season'], "episode": record['episode']}
		menu.add(30043, query, visible=validate_transmogrifier)
		query = {'mode': 'play_episode', "display": record['title'], "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "year": record['year'], "showtitle": record['showtitle'], "season": record['season'], "episode": record['episode']}
		plugin.add_video_item(query, record, total_items=count, image=record['cover_url'], fanart=record['backdrop_url'], menu=menu)
	plugin.eod(VIEWS.EPISODE_DEFAULT, 'tvshows')	
plugin.register('tv_calendar', tv_calendar)

def movie_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	if plugin.mode ==		'movie_watchlist'  or validate_trakt() is False:
		watchlist = []
	else:
		watchlist = trakt.get_watchlist_movies(simple=True)
	
	if plugin.mode ==		'movie_favorites':
		results = get_movie_favorites()
	elif plugin.mode ==		'movie_watchlist':
		results = trakt.get_watchlist_movies()
		results = sorted(results, key=lambda x: x['movie']['title'])
	elif plugin.mode ==		'movie_trending':
		results = trakt.get_trending_movies()
	elif plugin.mode ==		'movie_popular':
		results = trakt.get_popular_movies()
	elif plugin.mode ==		'movie_recommended':
		results = trakt.get_recommended_movies()
	elif plugin.mode ==		'movie_custom_list':
		results = trakt.get_custom_list(plugin.args['slug'], 'movie')
	elif plugin.mode == 	'movie_search':
		query = plugin.get_property('search.query.refesh')
		if query:
			plugin.clear_property('search.query')
			plugin.clear_property('search.query.refesh')
		else:
			query = plugin.dialog_input(i18n(30059))
		if query is None:
			plugin.clear_property("search.query")
			return
		plugin.set_property('search.query', query)
		results = trakt.search(query, 'movie')
	elif plugin.mode == 	'movie_similar':
		imdb_id = trakt.query_id('tmdb', plugin.args['tmdb_id']) if plugin.args['imdb_id'] == 'None' else plugin.args['imdb_id']
		results = trakt.get_similar_movies(imdb_id)
	count = len(results)
	if validate_trakt(): watched = trakt.get_watched_history('movies')
	if not results:
		return	
	for record in results:
		if plugin.mode  != 'movie_favorites':
			record = trakt.process_record(record, media='movie')
		else:
			record['cast'] = []
		menu = ContextMenu()
		menu.add(30045, {"mode": "movie_trailers", "tmdb_id": record['tmdb_id']}, script=True)
		menu.add(30046, {"mode": "movie_similar", "imdb_id": record['imdb_id']})
		menu.add(30047, {"mode": "import_movie", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "title": record['title']}, script=True, visible=validate_advanced)
		movie_title = record['title']
		if validate_trakt():
			if record['imdb_id'] in watched['imdb']:
				record['playcount'] = 1
				record['overlay'] = 7
				menu.add(30042, {"mode": "set_unwatched", "media": "movie", "id": record['imdb_id']})
			else:
				menu.add(30041, {"mode": "set_watched", "media": "movie", "id": record['imdb_id']})
		if plugin.mode ==	'movie_favorites':
			menu.add('Delete Favorite', {"mode": "delete_from_favorites", "media": "movie", "title": record['title'], "id": record['id']}, script=True, visible=validate_trakt()==False)
		else:
			menu.add('Save as Favorite', {"mode": "add_to_favorites", "media": "movie",  "record": record}, script=True, visible=validate_trakt()==False)
				
		if plugin.args['mode']=='movie_watchlist':
			menu.add(30037, {"mode": "movie_delete_from_watchlist", "imdb_id": record['imdb_id'], "name": movie_title}, script=True, visible=validate_trakt)
		else:
			if record['imdb_id'] in watchlist:
				record['title'] = '[COLOR %s]%s[/COLOR]' %  (WATCHLIST_COLOR, record['title'])
			menu.add(30038, {"mode": "movie_add_to_watchlist", "imdb_id": record['imdb_id']}, script=True, visible=validate_trakt)
			
		if plugin.args['mode']=='movie_custom_list':
			menu.add(30039, {"mode": "delete_from_custom_list", "media": "movie", "imdb_id": record['imdb_id'], "slug": plugin.args['slug'], "name": record['title']}, script=True, visible=validate_trakt)
		else:
			menu.add(30040, {"mode": "add_to_custom_list", "media": "movie", "imdb_id": record['imdb_id']}, script=True, visible=validate_trakt)	
		query = {'mode': 'movie_transmogrify', "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "year": record['year'], "title": movie_title }
		menu.add(30043, query, visible=validate_transmogrifier)
	
		plugin.add_video_item({'mode': 'play_movie', "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "year": record['year'], "title": movie_title}, record, menu=menu, total_items=count, image=record['cover_url'], fanart=record['backdrop_url'])
	plugin.eod(VIEWS.MOVIE_DEFAULT, 'movies')
plugin.register(['movie_watchlist', 'movie_trending', 'movie_popular', 'movie_recommended', 'movie_custom_list', 'movie_similar', 'movie_search', 'movie_favorites'], movie_list)

def discover_results():
	from dudehere.routines.tmdb import TMDB_API
	from dudehere.routines.trakt import TraktAPI
	tmdb = TMDB_API()
	trakt = TraktAPI()
	if validate_trakt():
		watchlist = trakt.get_watchlist_movies(simple=True, id='tmdb')
	else:
		watchlist = []
	query = ADDON.load_data('movie.discover.qs')
	page = int(plugin.args['page']) if 'page' in plugin.args.keys() else query['page']
	query['page'] = page
	results = tmdb.discover_movies(query)
	total_pages = results['total_pages']
	count = len(results)
	#plugin.add_menu_item({'mode': 'movie_menu'}, {'title': '[COLOR %s]Movies Menu[/COLOR]' % PREVIOUSPAGE_COLOR}, image=ARTWORK +"movies.jpg")
	#if page >1: plugin.add_menu_item({'mode': 'discover_results', "page": page - 1}, {'title': '[COLOR %s]<< Previous Page %s/%s[/COLOR]' % (PREVIOUSPAGE_COLOR, page - 1, total_pages)}, image=ARTWORK +"previous_page.jpg")
	for result in results['results']:
		record = tmdb.process_record(result, 'movie')
		movie_title = record['title']
		menu = ContextMenu()
		menu.add(30045, {"mode": "movie_trailers", "tmdb_id": record['tmdb_id']}, script=True)
		menu.add(30046, {"mode": "movie_similar", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id']})
		menu.add(30047, {"mode": "import_movie", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "title": record['title']}, script=True, visible=validate_advanced)
		menu.add('Save as Favorite', {"mode": "add_to_favorites", "media": "movie",  "record": record}, script=True, visible=validate_trakt()==False)
	
		if int(record['tmdb_id']) in watchlist:
			record['title'] = '[COLOR %s]%s[/COLOR]' % (WATCHLIST_COLOR, record['title'])
			menu.add(30037, {"mode": "movie_delete_from_watchlist", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "name": movie_title}, script=True, visible=validate_trakt)
		else:
			menu.add(30038, {"mode": "movie_add_to_watchlist", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id']}, script=True, visible=validate_trakt)
		menu.add(30040, {"mode": "add_to_custom_list", "media": "movie", "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id']}, script=True, visible=validate_trakt)
		plugin.add_video_item({'mode': 'play_movie', "imdb_id": record['imdb_id'], "tmdb_id": record['tmdb_id'], "year": record['year'], "title": movie_title}, record, menu=menu, total_items=count, image=record['cover_url'], fanart=record['backdrop_url'])
	if total_pages > 1: plugin.add_menu_item({'mode': 'discover_results', "page": page+1}, {'title': i18n(30060) % (NEXTPAGE_COLOR, page+1, total_pages)}, image=ARTWORK +"next_page.jpg")
	plugin.eod(VIEWS.MOVIE_DEFAULT, 'movies')
plugin.register('discover_results', discover_results)



def get_tv_favorites():
	records = []
	plugin.DB.connect()
	results = plugin.DB.query_assoc("SELECT * FROM tvshow_favorites ORDER BY title ASC", force_double_array=True)
	plugin.DB.disconnect()
	if results:
		return results
	else:
		plugin.notify('Favorites is empty', 'Add something to the list!')
		return records
	
def get_movie_favorites():
	records = []
	plugin.DB.connect()
	results = plugin.DB.query_assoc("SELECT * FROM movie_favorites ORDER BY title ASC", force_double_array=True)
	plugin.DB.disconnect()
	if results:
		return results
	else:
		plugin.notify('Favorites is empty', 'Add something to the list!')
		return records

def add_to_favorites():
	import ast
	record = plugin.args['record']
	record = ast.literal_eval(record)
	if plugin.args['media'] == 'tvshow':
		SQL = """INSERT OR REPLACE INTO tvshow_favorites (
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
				trailer_url
				) VALUES(?,?,?,?,? ,?,?,?,?,?, ?,?,?,?,?, ?)
				"""
				
		values = [record[k] for k in ["imdb_id","tmdb_id","tvdb_id","trakt_id","slug","title","year","TVShowTitle","duration","rating","plot","mpaa","cover_url","banner_url","backdrop_url","trailer_url"]]
	else:
		SQL = """INSERT OR REPLACE INTO movie_favorites (
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
				trailer_url
				) VALUES(?,?,?,?,?, ?,?,?,?,?, ?,?,?,?,?, ?,?)
				"""
		values = [record[k] for k in ["imdb_id","tmdb_id","trakt_id","slug", "title","year","tagline","duration","rating","votes","plot","mpaa","premiered","cover_url","thumb_url","backdrop_url","trailer_url"]]
	plugin.DB.connect()
	plugin.DB.execute(SQL, values)
	plugin.DB.commit()
	plugin.DB.disconnect()	
	plugin.notify('Success', 'Added Favorite: %s' % record['title'])
	#plugin.refresh()

plugin.register('add_to_favorites', add_to_favorites)

def delete_from_favorites():
	ok = plugin.confirm('Delete favorite', "click YES to continue", plugin.args['title'])
	if ok:
		plugin.DB.connect()
		SQL = "DELETE FROM %s_favorites WHERE id=?" % plugin.args['media']
		plugin.DB.execute(SQL, [plugin.args['id']])
		plugin.DB.commit()
		plugin.DB.disconnect()
		plugin.notify('Success', 'Favorite deleted: %s' % plugin.args['title'])
		plugin.refresh()

plugin.register('delete_from_favorites', delete_from_favorites)


def toggle_watched():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	re_watchlist = False
	if plugin.mode == 'set_watched':
		watched = True
		if plugin.args['media'] == 'episode' or plugin.args['media'] == 'season':
			watchlist = trakt.get_watchlist_tvshows(simple=True)
			re_watchlist = plugin.args['imdb_id'] in watchlist
	else:
		watched = False
	if plugin.args['media'] == 'season':
		trakt.set_watched_state(plugin.args['media'], plugin.args['imdb_id'], watched, plugin.args['id'])
	else:
		trakt.set_watched_state(plugin.args['media'], plugin.args['id'], watched)
	if re_watchlist: trakt.add_to_watchlist('shows', plugin.args['imdb_id'], id_type='imdb')
	plugin.notify(i18n(33019), i18n(30061) if watched == True else in18(30062))
	plugin.refresh()
plugin.register(['set_watched', 'set_unwatched'], toggle_watched)	

def set_watched(media, imdb_id, season=None, episode=None):
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	if media == 'episode':
		re_watchlist = False
		watchlist = trakt.get_watchlist_tvshows(simple=True)
		re_watchlist = imdb_id in watchlist
		episode =trakt.get_episode_details(imdb_id, season, episode, None)
		trakt_id = episode['trakt_id']
		trakt.set_watched_state(media, trakt_id, True)
		if re_watchlist: trakt.add_to_watchlist('shows', imdb_id, id_type='imdb')
	plugin.refresh()

def custom_list_menu():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	lists = trakt.get_custom_lists()
	media = 'tv' if plugin.mode == 'tv_custom_lists' else 'movie'
	DB.connect()
	results = DB.query("SELECT slug FROM lists WHERE media=?", [media], force_double_array=True)
	DB.disconnect()
	sync_lists = [l[0] for l in results]
	plugin.add_menu_item({'mode': 'new_custom_list', "media": media}, {"title": '***New Custom List***'}, image=ARTWORK+'/create_trakt_list.jpg')
	for list in lists:
		menu = ContextMenu()
		if list['ids']['slug'] in sync_lists:
			display = "[COLOR %s]%s[/COLOR]" % (SYNC_COLOR, list['name'])
			menu.add(30048, {"mode": "unsync_list", "slug": list['ids']['slug'], "name": list['name']}, script=True, visible=validate_advanced)
		else:
			display = list['name']
			menu.add(30049, {"mode": "sync_%s_list" % media, "slug": list['ids']['slug'], "name": list['name']}, script=True, visible=validate_advanced)
		
		menu.add(30050, {"mode": "delete_custom_list", "slug": list['ids']['slug'], "name": list['name']}, script=True)
		plugin.add_menu_item({"mode": media + "_custom_list", 'slug': list['ids']['slug'], "media": media}, {"title": display}, menu=menu)
	plugin.eod(VIEWS.LIST)
plugin.register(['tv_custom_lists', 'movie_custom_lists'], custom_list_menu)


def update_subscription(imdb_id):
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	vfs = VFSClass()
	show = trakt.get_show_info(imdb_id, False)
	series = vfs.clean_file_name(show['title'])
	show_path = vfs.join(TVSHOW_DIRECTORY, series, preserve=False)
	vfs.mkdir(show_path, recursive=True)
	show = trakt.get_show_info(imdb_id, True)
	for row in show:
		if 'episodes' in row.keys():
			season = row['episodes'][0]['season']
			if season > 0:
				season_path = vfs.join(show_path, "Season %s" % season, preserve=False)
				vfs.mkdir(season_path)
				for ep in row['episodes']:
					doit = True
					if ADDON.get_setting('import_aired_only')=='true':
						doit = check_air_date(ep['first_aired'])
					if doit:
						episode = ep['number']
						filename = "%s S%sE%s.strm" % (series, str(season).zfill(2), str(episode).zfill(2))
						full_path =  vfs.join(season_path, filename, preserve=False)
						params = {"mode": "watch_stream", "media": "episode", "imdb_id": imdb_id, "season":season, "episode": episode, "trakt": ep['ids']['trakt']}
						url = plugin.build_plugin_url(params)
						create_str_file(full_path, url)
						
def autoupdate_tv():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	DB.connect()
	results = DB.query("SELECT imdb_id FROM subscriptions WHERE enabled=1 ORDER BY title ASC", force_double_array=True)
	for result in results:
		update_subscription(result[0])
	results = DB.query("SELECT media, slug FROM lists WHERE media='tv' AND sync=1", force_double_array=True)
	for result in results:
		shows = trakt.get_custom_list(result[1], result[0], params={})
		for show in shows:
			imdb_id = show['show']['ids']['imdb']
			if imdb_id is None: continue
			update_subscription(imdb_id)
	DB.disconnect()	
plugin.register('autoupdate_tv', autoupdate_tv)

def autoupdate_movie():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	DB.connect()
	results = DB.query("SELECT media, slug FROM lists WHERE media='movie' AND sync=1", force_double_array=True)
	
	for result in results:
		movies = trakt.get_custom_list(result[1], result[0], params={})
		for movie in movies:
			imdb_id = movie['movie']['ids']['imdb']
			if imdb_id is None: continue
			import_movie(imdb_id, movie['movie']['title'], True)
	DB.disconnect()
plugin.register('autoupdate_movie', autoupdate_movie)

def update_all():
	autoupdate_tv()
	autoupdate_movie()
	plugin.notify(i18n(30063), i18n(33064))
plugin.register('update_all', update_all)

def check_air_date(aired):
	if aired:
		from datetime import date
		now = date.today()
		match = re.search('^(.+?)-(.+?)-(.+?)T', aired)
		y = int(match.group(1))
		m = int(match.group(2))
		d = int(match.group(3))
		aired = date(y,m,d)
		if aired < now:
			return True
		else: 
			return False

def create_str_file(full_path, url):
	vfs = VFSClass()
	create_file = True
	if ADDON.get_setting('overwrite_strm_files')=='false':
		if vfs.exists(full_path):
			create_file = False
	if create_file:
		file = vfs.open(full_path,'w')
		file.write(url)
		file.close()

def manage_subscriptions():
	DB.connect()
	results = DB.query("SELECT id, title, enabled FROM subscriptions ORDER BY title ASC", force_double_array=True)
	DB.disconnect()
	for result in results:
		menu = ContextMenu()
		if result[2] == 1:
			display = result[1]
		else:
			display = "[COLOR %s]%s[/COLOR]" % (DISABLED_COLOR, result[1])
		menu.add(30051, {"mode": "unsubscribe", "id": result[0], "title": result[1]}, script=True)
		plugin.add_menu_item({"mode": "toggle_subscription", 'id': result[0]}, {"title": display}, menu=menu)
	plugin.eod(VIEWS.LIST)	
plugin.register('manage_subscriptions', manage_subscriptions)

def toggle_subscription():
	id = plugin.args['id']
	DB.connect()
	DB.execute("UPDATE subscriptions SET enabled=(enabled * -1) + 1 WHERE id=?", [id])
	DB.commit()
	DB.disconnect()
	plugin.refresh()
plugin.register("toggle_subscription", toggle_subscription)

def subscribe():
	imdb_id = plugin.args['imdb_id']
	title = plugin.args['title']
	DB.connect()
	DB.execute("INSERT INTO subscriptions(imdb_id, title) VALUES(?,?)", [imdb_id, title])
	DB.commit()
	DB.disconnect()
	update_subscription(imdb_id)
	plugin.notify(i18n(30065), title)
plugin.register('subscribe', subscribe)

def unsubscribe():
	id = plugin.args['id']
	title = plugin.args['title']
	ok = plugin.confirm(i18n(30066), title)
	if ok:
		DB.connect()
		DB.execute("DELETE FROM subscriptions WHERE id=?", [id])
		DB.commit()
		DB.disconnect()
		plugin.notify(i18n(30067), title)
		plugin.refresh()
plugin.register('unsubscribe', unsubscribe)

def import_movie(imdb_id=None, title=None, quiet=False):
	vfs = VFSClass()
	if imdb_id is None:
		from dudehere.routines.trakt import TraktAPI
		trakt = TraktAPI()
		imdb_id = trakt.query_id('tmdb', plugin.args['tmdb_id']) if plugin.args['imdb_id'] == 'None' else plugin.args['imdb_id']
	title = title if title is not None else plugin.args['title']
	movie_title = vfs.clean_file_name(title)
	movie_path = vfs.join(MOVIE_DIRECTORY, movie_title, preserve=False)
	vfs.mkdir(movie_path, recursive=True)
	filename = "%s.strm" % movie_title
	full_path =  vfs.join(movie_path, filename, preserve=False)
	params = {"mode": "watch_stream", "media": "movie", "imdb_id": imdb_id}
	url = plugin.build_plugin_url(params)
	create_str_file(full_path, url)
	if not quiet:
		plugin.notify(i18n(30068), title)
plugin.register('import_movie', import_movie)

def sync_list():
	media = 'movie' if plugin.mode == 'sync_movie_list' else 'tv'
	slug = plugin.args['slug']
	name = plugin.args['name']
	DB.connect()
	DB.execute("INSERT INTO lists(list, slug, media) VALUES(?,?,?)", [name, slug, media])
	DB.commit()
	DB.disconnect()
	plugin.notify(i18n(30069), name)
	plugin.refresh()
plugin.register(['sync_tv_list', 'sync_movie_list'], sync_list)

def unsync_list():
	slug = plugin.args['slug']
	name = plugin.args['name']
	ok = plugin.confirm(i18n(30070), name)
	if ok:
		DB.connect()
		DB.execute("DELETE FROM lists WHERE slug=?", [slug])
		DB.commit()
		DB.disconnect()
		plugin.notify(i18n(30071), name)
		plugin.refresh()
plugin.register('unsync_list', unsync_list)

def new_custom_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	name = plugin.dialog_input(i18n(30072))
	if name:
		response = trakt.create_custom_list(name)
		if 'ids' in response.keys():
			plugin.notify(i18n(33019), i18n(30073), image=ARTWORK + 'trakt.png')
		else:
			plugin.notify(i18n(33020), i18n(30074), image=ARTWORK + 'trakt.png')
		plugin.refresh()
plugin.register('new_custom_list', new_custom_list)

def delete_custom_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	ok = plugin.confirm(i18n(30075), i18n(30076), plugin.args['name'])
	if ok:
		response = trakt.delete_custom_list(plugin.args['slug'])
		if response:
			plugin.refresh()
		else:
			plugin.notify(i18n(33020), i18n(30074), image=ARTWORK + 'trakt.png')

plugin.register('delete_custom_list', delete_custom_list)

def delete_from_custom_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	ok = plugin.confirm(i18n(30077), i18n(30076), plugin.args['name'])
	if plugin.args['media'] == 'movie':
		media = 'movies'
	else:
		media = 'shows'
	if ok:
		response = trakt.delete_from_custom_list(plugin.args['media'], plugin.args['slug'], plugin.args['imdb_id'])
		print response
		plugin.refresh()
		if response['deleted'][media]==1:
			plugin.notify(i18n(33019), i18n(30078), image=ARTWORK + 'trakt.png')
		elif response['not_found'][media]==1:
			plugin.notify(i18n(33028), i18n(30079), image=ARTWORK + 'trakt.png')
		else:
			plugin.notify(i18n(33020), i18n(30074), image=ARTWORK + 'trakt.png')
plugin.register('delete_from_custom_list', delete_from_custom_list)

def add_to_custom_list():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	lists = trakt.get_custom_lists()
	options = [lists[index]['name'] for index in xrange(len(lists))]
	index = plugin.dialog_select(i18n(30080), options)
	if plugin.args['media'] == 'movie':
		media = 'movies'
	else:
		media = 'shows'
	if index:
		slug = lists[index]['ids']['slug']
		if plugin.args['imdb_id'] == None or plugin.args['imdb_id'] == 'None':
			id = plugin.args['tmdb_id']
			id_type = 'tmdb'
		else:
			id = plugin.args['imdb_id']
			id_type = 'imdb'
		response = trakt.add_to_custom_list(plugin.args['media'], slug, id, id_type)
		if response['added'][media]==1:
			plugin.notify(i18n(33019), i18n(30081), image=ARTWORK + 'trakt.png')
		elif response['existing'][media]==1:
			plugin.notify(i18n(33028), 'Already exists in list', image=ARTWORK + 'trakt.png')
		else:
			plugin.notify(i18n(33020), i18n(30074), image=ARTWORK + 'trakt.png')
plugin.register('add_to_custom_list', add_to_custom_list)	

def add_watchlist():
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	if plugin.mode == 'tv_add_to_watchlist':
		media = 'shows'
	else:
		media = 'movies'
	if plugin.args['imdb_id'] == None or plugin.args['imdb_id'] == 'None':
		id = plugin.args['tmdb_id']
		id_type = 'tmdb'
	else:
		id = plugin.args['imdb_id']
		id_type = 'imdb'
	response = trakt.add_to_watchlist(media, id, id_type=id_type)
	if response['added'][media]==1:
		plugin.refresh()
		plugin.notify(i18n(33019), i18n(30082), image=ARTWORK + 'trakt.png')
	elif response['existing'][media]==1:
		plugin.notify(i18n(33028), i18n(30083), image=ARTWORK + 'trakt.png')
	else:
		plugin.notify(i18n(33020), i18n(30074), image=ARTWORK + 'trakt.png')
plugin.register(['tv_add_to_watchlist', 'movie_add_to_watchlist'], add_watchlist)

def delete_from_watchlist():
	from dudehere.routines.trakt import TraktAPI
	print plugin.args
	trakt = TraktAPI()
	if plugin.mode == 'tv_delete_from_watchlist':
		media = 'shows'
	else:
		media = 'movies'
	ok = plugin.confirm(i18n(30084), i18n(30076), plugin.args['name'])
	if ok:
		if plugin.args['imdb_id'] == None or plugin.args['imdb_id'] == 'None':
			id = plugin.args['tmdb_id']
			id_type = 'tmdb'
		else:
			id = plugin.args['imdb_id']
			id_type = 'imdb'
		response = trakt.delete_from_watchlist(media, id, id_type=id_type)

		if response['deleted'][media]==1:
			plugin.refresh()
			plugin.notify(i18n(33019), i18n(30085), image=ARTWORK + 'trakt.png')
		elif response['not_found'][media]==1:
			plugin.notify(i18n(33028), i18n(30086), image=ARTWORK + 'trakt.png')
		else:
			plugin.notify(i18n(33020), i18n(30076), image=ARTWORK + 'trakt.png')
		
plugin.register(['tv_delete_from_watchlist', 'movie_delete_from_watchlist'], delete_from_watchlist)

def movie_trailers():
	from dudehere.routines.tmdb import TMDB_API
	tmdb = TMDB_API()
	trailers = tmdb.movie_trailers(plugin.args['tmdb_id'])
	options = [trailers[index]['name'] for index in xrange(len(trailers))]
	index = plugin.dialog_select(i18n(30087), options)
	if index is not False:
		key = trailers[index]['key']
		plugin.play_url('plugin://plugin.video.youtube/play/?video_id=' + key)
plugin.register('movie_trailers', movie_trailers)

def show_help():
	vfs = VFSClass()
	content = vfs.read_file(vfs.join(LANGUAGE_PATH, 'help.txt'))
	plugin.show_textbox(i18n(30088), content)
plugin.register('show_help', show_help)

def advanced_mode():
	mode = 'false' if validate_advanced() else 'true'
	for i in range(1,8):
		ADDON.set_setting('advanced_mode_%s' % i, mode)
	plugin.refresh()
plugin.register('advanced_mode', advanced_mode)

def set_language():
	from dudehere.routines.window import Window
	vfs = VFSClass()
	class LanguageWindow(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title, width=650, height=500, columns=3, rows=8)
			
		def set_info_controls(self):
			from resources.lib.language import LanguageClass
			lang = LanguageClass()
			def set_lang():
				obj = self.getFocus()
				for index in xrange(self.get_object('language').size()):
					selected = self.get_object('language').getListItem(index).getLabel2()
					if selected:
						self.get_object('language').getListItem(index).setLabel(selected)
						self.get_object('language').getListItem(index).setLabel2('')
				#
				language = obj.getSelectedItem().getLabel()
				obj.getSelectedItem().setLabel('[B][COLOR %s]%s[/COLOR][/B]' % (ENABLED_COLOR, language))
				obj.getSelectedItem().setLabel2(language)
				code = lang.get_code_by_lang(language)
				if code:
					ADDON.set_setting('alluc_api_language', code)
				else:
					ADDON.set_setting('alluc_api_language', '')
				
			self.add_label(self.create_label(i18n(33002)), 0, 0, columnspan=3, rowspan=3, pad_x=15, pad_y=10)
			self.create_list('language')
			self.add_object('language', 1,0,7,3)
			self.add_list_items('language', lang.get_languages(), selectable=False, call_back=set_lang)
			current = ADDON.get_setting('alluc_api_language')
			for index in xrange(self.get_object('language').size()):
				language = self.get_object('language').getListItem(index).getLabel()
				code = lang.get_code_by_lang(language)
				if code:
					icon = vfs.join(ARTWORK, 'flags/%s.png' % code)
					self.get_object('language').getListItem(index).setIconImage(icon)
				if code == current:
					self.get_object('language').getListItem(index).setLabel('[B][COLOR %s]%s[/COLOR][/B]' % (ENABLED_COLOR, language))
					self.get_object('language').getListItem(index).setLabel2(language)
			if current == '':
				language = self.get_object('language').getListItem(0).getLabel()
				self.get_object('language').getListItem(0).setLabel('[B][COLOR %s]%s[/COLOR][/B]' % (ENABLED_COLOR, language))
				self.get_object('language').getListItem(0).setLabel2(language)
			
			self.create_button('close', 'Close')
			self.add_object('close', 7, 1)
			self.set_focus('language')
			self.set_object_event('down', 'language', 'close')
			self.set_object_event('right', 'language', 'close')
			self.set_object_event('up', 'close', 'language')
			self.set_object_event('action', "close", self.close)
				
	L = LanguageWindow(i18n(33029))
	L.show()
	del L
plugin.register("set_language", set_language)

def reset_alluc():
	from dudehere.routines.window import Window
	class ResetWindow(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title,width=700, height=300, columns=4, rows=6)
			self.draw()
			
		def set_info_controls(self):
			
			label = self.create_label(i18n(33031))
			self.add_label(label, 0, 0, columnspan=4, pad_x=15, pad_y=10)
			
			label = self.create_label(i18n(33032))
			self.add_label(label, 1, 0, columnspan=4, pad_x=15, pad_y=10)
			
			label = self.create_label(i18n(33033))
			self.add_label(label, 2, 0, columnspan=4, pad_x=15, pad_y=10)
			
			label = self.create_label(i18n(33034))
			self.add_label(label, 3, 0, columnspan=4, pad_x=15, pad_y=10)
			
			label = self.create_label(i18n(33035))
			self.add_label(label, 4, 0, columnspan=2, pad_x=15, pad_y=10)
			
			self.create_input('reset', _alignment=2)
			self.add_object('reset', 4, 1, columnspan=2)
			
			self.create_button('cancel', i18n(33036))
			self.add_object('cancel',  5, 1)
			
			self.create_button('confirm', i18n(33037))
			self.add_object('confirm',  5, 2)
			
		def confirm(self):
			if self.get_value('reset') != 'RESET':
				plugin.notify(i18n(33039), i18n(33040))
				return
			ok = plugin.confirm(i18n(33041), i18n(33042), i18n(33043))
			if ok:
				VFSClass().rm(DATA_PATH, quiet=True, recursive=True)
				self.close()
				plugin.exit()
			else:
				self.close()
			self.close()
		
	reset = ResetWindow(i18n(33044))
	reset.set_object_event('focus', 'reset')
	reset.set_object_event('down', 'reset', 'confirm')
	reset.set_object_event('up', 'confirm', 'reset')
	reset.set_object_event('left', 'confirm', 'cancel')
	reset.set_object_event('right', 'cancel', 'confirm')
	reset.set_object_event('up', 'cancel', 'reset')
	reset.set_object_event('action', 'cancel', reset.close)
	reset.set_object_event('action', 'confirm', reset.confirm)
	reset.show()
plugin.register("reset_alluc", reset_alluc)

def authorize_trakt():
	from dudehere.routines.window import Window
	class AuthorizeWindow(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title, width=800, height=400, columns=4, rows=6)
			
		def authorize(self):
			pin = self.get_value('pin')
			from dudehere.routines.trakt import TraktAPI
			trakt = TraktAPI()
			response = trakt.authorize(pin)
			if response:
				settings = trakt.get_settings()
				if settings:
					ADDON.set_setting('trakt_account', settings['user']['username'])
				self.get_object('authorized').setVisible(True)
				plugin.notify(i18n(33045), i18n(33019), image=ARTWORK + "trakt.png")
				self.close()
				plugin.refresh()
			else:
				ADDON.set_setting('trakt_account', '')
				plugin.notify(i18n(33045), i18n(33020), image=ARTWORK + "trakt.png")

		def set_info_controls(self):
			self.create_image('trakt', ARTWORK + 'trakt.png', aspectRatio=1)
			self.add_object('trakt', 0, 0, columnspan=3, rowspan=3)
			
			self.add_label(self.create_label(i18n(33008)), 0, 0, columnspan=3, rowspan=3, pad_x=15, pad_y=10)
			
			self.add_label(self.create_label(i18n(33009) % ADDON.get_setting('trakt_pin_url')), 3, 0, columnspan=3, rowspan=2, pad_x=15, pad_y=10)
			
			self.create_input('pin', _alignment=2)
			self.add_object('pin', 4, 0, columnspan=3)
			
			self.create_image('qr_code', ARTWORK + 'qr_code.png', aspectRatio=2)
			self.add_object('qr_code', 0, 3, columnspan=1, rowspan=2)
			
			self.create_image('authorized', ARTWORK + 'checked.png', aspectRatio=2)
			self.add_object('authorized', 2, 3)
			self.get_object('authorized').setVisible(False)
			
			self.create_button('authorize', i18n(33017))
			self.add_object('authorize', 4, 3)	
			self.set_object_event('action', "authorize", self.authorize)
			
			self.create_button('cancel', i18n(33013))
			self.add_object('cancel', 5, 0)	
			self.set_object_event('action', "cancel", self.close)
			
			self.set_focus('pin')
			self.set_object_event('left', 'authorize', 'pin')
			self.set_object_event('right', 'pin', 'authorize')
			self.set_object_event('down', 'authorize', 'cancel')
			self.set_object_event('down', 'pin', 'cancel')
			self.set_object_event('up', 'cancel', 'pin')

			
	A = AuthorizeWindow(i18n(33046))
	A.show()
	del A
plugin.register('authorize_trakt', authorize_trakt)	

def color_picker():
	vfs = VFSClass()
	colors = vfs.read_file(vfs.join(ROOT_PATH, 'resources/colors.txt')).splitlines()
	display = []
	for color in colors:
		color = color.lower()
		display.append("[COLOR %s]%s[/COLOR]" % (color, color))
	index = plugin.dialog_select(i18n(30089), display)
	if not index: return
	color = colors[index].lower()
	ADDON.set_setting('custom_color_%s' % plugin.args['type'], color)
plugin.register('color_picker', color_picker)

def open_settings():
	xbmcaddon.Addon(id=plugin.args['addon_id']).openSettings()
plugin.register(['alluc_settings', 'urlresolver_settings'], open_settings)

def add_source_folders():
	from BeautifulSoup import BeautifulSoup, Tag
	vfs = VFSClass()
	if not vfs.exists(TVSHOW_DIRECTORY): vfs.mkdir(TVSHOW_DIRECTORY)
	if not vfs.exists(MOVIE_DIRECTORY): vfs.mkdir(MOVIE_DIRECTORY)
	source_path = vfs.join('special://profile/', 'sources.xml')
	try:
		soup = vfs.read_file(source_path, soup=True)
	except:
		soup = BeautifulSoup()
		sources_tag = Tag(soup, "sources")
		soup.insert(0, sources_tag)
		
	if soup.find("video") == None:
		sources = soup.find("sources")
		video_tag = Tag(soup, "video")
		sources.insert(0, video_tag)
		
	video = soup.find("video")
	if len(soup.findAll(text="Movies (%s)" % ADDON_NAME)) < 1:
		movie_source_tag = Tag(soup, "source")
		movie_name_tag = Tag(soup, "name")
		movie_name_tag.insert(0, "Movies (%s)" % ADDON_NAME)
		MOVIES_PATH_tag = Tag(soup, "path")
		MOVIES_PATH_tag['pathversion'] = 1
		MOVIES_PATH_tag.insert(0, MOVIE_DIRECTORY)
		movie_source_tag.insert(0, movie_name_tag)
		movie_source_tag.insert(1, MOVIES_PATH_tag)
		video.insert(2, movie_source_tag)

	if len(soup.findAll(text="TV Shows (%s)" % ADDON_NAME)) < 1:	
		tvshow_source_tag = Tag(soup, "source")
		tvshow_name_tag = Tag(soup, "name")
		tvshow_name_tag.insert(0, "TV Shows (%s)" % ADDON_NAME)
		tvshow_path_tag = Tag(soup, "path")
		tvshow_path_tag['pathversion'] = 1
		tvshow_path_tag.insert(0, TVSHOW_DIRECTORY)
		tvshow_source_tag.insert(0, tvshow_name_tag)
		tvshow_source_tag.insert(1, tvshow_path_tag)
		video.insert(2, tvshow_source_tag)
	string = ""
	for i in soup:
		string = string + str(i)
	vfs.write_file(source_path, str(soup))
	plugin.dialog_ok(i18n(30090), i18n(30091), i18n(30092), i18n(30093))
plugin.register('add_source_folders', add_source_folders)

def quick_search():
	query = plugin.dialog_input(i18n(30094))
	if query is None: return
	from dudehere.routines.scrapers import CommonScraper
	Scraper = CommonScraper(load=['alluc_api'])
	results = Scraper.get_scraper_by_index(0).quick_search(query)
	Scraper.process_results(results)
	raw_url = Scraper.select_stream()
	if raw_url:
		resolved_url = Scraper.resolve_url(raw_url)
	else: return
	if not resolved_url: return
	plugin.play_stream(resolved_url, metadata={"title": i18n(30094), "cover_url": ""}, title=query)
	
plugin.register('quick_search', quick_search)

def movie_advanced_search():
	from dudehere.routines.window import Window
	from dudehere.routines.tmdb import TMDB_API, MOVIE_GENRES as GENRES
	tmdb = TMDB_API()
	
	class DiscoverWindow(Window):
		def __init__(self, title):
			super(self.__class__,self).__init__(title,width=750, height=525, columns=4, rows=9)
			self.draw()
		
		def set_info_controls(self):
			self.add_label(self.create_label(i18n(30095), textColor="0xFF0088FF"), 0, 2,  pad_x=42, pad_y=30)
			items = ["G", "PG", "PG-13", "R", "NC-17"]
			self.create_list('rating')
			self.add_object('rating', 1,2,6,1)
			self.add_list_items('rating', items, allow_multiple=False, allow_toggle=True)
			
			
			self.add_label(self.create_label(i18n(30096), textColor="0xFF0088FF"), 0, 3,  pad_x=42, pad_y=30)
			items = [GENRES.r_map[id].lower() for id in GENRES.r_map.keys()]
			self.create_list('genre')
			self.add_object('genre', 1,3,7,1)
			self.add_list_items('genre', items, allow_multiple=True, allow_toggle=True)
			
			self.add_label(self.create_label(i18n(30095), textColor="0xFF0088FF"), 0, 0, pad_x=15, pad_y=30)
			self.create_input('keyword')
			self.add_object('keyword', 1, 0, columnspan=2, pad_x=15)
			
			self.add_label(self.create_label(i18n(30098), textColor="0xFF0088FF"), 2, 0,  pad_x=15, pad_y=30)
			self.create_input('actor')
			self.add_object('actor', 3, 0, columnspan=2, pad_x=15)
			
			self.add_label(self.create_label(i18n(30099), textColor="0xFF0088FF"), 4, 0, pad_x=15, pad_y=30)
			items = ["Popularity", "Release Date", "User Rating", "Revenue"]
			self.create_list('sorting')
			self.add_object('sorting', 5,0,3,2)
			self.add_list_items('sorting', items, 0, allow_multiple=False, allow_toggle=False)
			
			self.create_button('cancel', i18n(33013))
			self.add_object('cancel',  8, 1)
			
			self.create_button('discover', i18n(33047))
			self.add_object('discover',  8, 2)
	
										
	def discover():
		actor = w.get_value('actor')
		keyword = w.get_value('keyword')
		genre = w.get_value('genre', return_text=True)
		rating = w.get_value('rating', return_text=True)
		sorting = w.get_value('sorting', return_index=True)
		sorting = ["popularity.desc", "release_date.desc", "vote_average.desc", "revenue.desc"][sorting[0]]
		query = {"sort_by": sorting, "page": 1}
		if keyword:
			keyword_ids = tmdb.query_keyword_id(keyword)
			if len(keyword_ids) > 0:
				query['with_keywords'] = "|".join(keyword_ids)
		if actor:
			actor_ids = tmdb.query_person_id(actor)
			if len(actor_ids) > 0:
				query['with_cast'] = "|".join(actor_ids)
		if len(rating) > 0:
			query['certification_country'] = 'US'
			query['certification.lte'] = rating[0]
		genres = []	
		for text in genre:
			id = GENRES.f_map[text.upper()]
			genres.append(str(id))
		if len(genres) > 0:
			query['with_genres'] = "|".join(genres)	
		w.close()
		query = ADDON.save_data('movie.discover.qs', query)
		plugin.navigate_to({"mode": "discover_results"})
		
	w = DiscoverWindow(i18n(33047))
	w.set_object_event('action', 'cancel', w.close)
	w.set_object_event('action', 'discover', discover)
	w.set_object_event('focus', 'keyword')
	w.set_object_event('down', 'keyword', 'actor')
	w.set_object_event('down', 'actor', 'sorting')
	w.set_object_event('down', 'sorting', 'discover')
	w.set_object_event('down', 'rating', 'discover')
	w.set_object_event('down', 'genre', 'discover')
	w.set_object_event('right', 'keyword', 'rating')
	w.set_object_event('right', 'actor', 'rating')
	w.set_object_event('right', 'rating', 'genre')
	w.set_object_event('right', 'sorting', 'rating')
	w.set_object_event('left', 'genre', 'rating')
	w.set_object_event('left', 'rating', 'keyword')
	
	w.set_object_event('left', 'discover', 'cancel')
	w.set_object_event('up', 'actor', 'keyword')
	w.set_object_event('up', 'sorting', 'actor')
	w.set_object_event('up', 'cancel', 'sorting')
	w.set_object_event('up', 'discover', 'sorting')
	w.show()
	
plugin.register('movie_advanced_search', movie_advanced_search)

def on_playback_stop():
	if validate_trakt() is False: return
	if 'imdb_id' in plugin.args.keys():
		data= plugin.get_stream_stop_times()
		media = 'episode' if plugin.mode in ['play_episode'] else 'movie'
		imdb_id = plugin.args['imdb_id']
		if data['percent'] >= WATCH_PERCENT:
			if media == 'episode':
				season = plugin.args['season']
				episode = plugin.args['episode']
				set_watched(media, imdb_id, season, episode)
			else:
				set_watched(media, imdb_id)	
plugin.on_playback_stop = on_playback_stop

def play_episode():
	from dudehere.routines.scrapers import CommonScraper
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	Scraper = CommonScraper(load=['alluc_api'], cache_results=ADDON.get_setting('enable_result_caching')=="true")
	imdb_id = trakt.query_id('tmdb', plugin.args['tmdb_id']) if plugin.args['imdb_id'] == 'None' else plugin.args['imdb_id']
	title = plugin.args['showtitle']
	display = plugin.args['display']
	season = int(plugin.args['season'])
	episode = int(plugin.args['episode'])
	year = int(plugin.args['year'])
	resolved_url = Scraper.search_tvshow(title, season, episode, year, imdb_id)
	if not resolved_url: return
	metadata = trakt.get_episode_details(imdb_id, season, episode)
	plugin.play_stream(resolved_url, metadata=metadata, title=display)
plugin.register('play_episode', play_episode)

def play_movie():
	from dudehere.routines.scrapers import CommonScraper
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	Scraper = CommonScraper(load=['alluc_api'], cache_results=ADDON.get_setting('enable_result_caching')=="true")
	imdb_id = trakt.query_id('tmdb', plugin.args['tmdb_id']) if plugin.args['imdb_id'] == 'None' else plugin.args['imdb_id']
	title = plugin.args['title']
	year = plugin.args['year']
	metadata = trakt.get_movie_details(imdb_id)
	resolved_url = Scraper.search_movie(title, year, imdb_id=imdb_id)
	if not resolved_url: return
	plugin.play_stream(resolved_url, metadata=metadata)
plugin.register('play_movie', play_movie)

def watch_stream():
	from dudehere.routines.scrapers import CommonScraper
	from dudehere.routines.trakt import TraktAPI
	trakt = TraktAPI()
	Scraper = CommonScraper(load=['alluc_api'], cache_results=ADDON.get_setting('enable_result_caching')=="true")
	imdb_id = plugin.args['imdb_id']
	if plugin.args['media'] == 'episode':
		season = int(plugin.args['season'])
		episode = int(plugin.args['episode'])
		metadata = trakt.get_episode_details(imdb_id, season, episode)
		year = metadata['year']
		title = metadata['showtitle']
		resolved_url = Scraper.search_tvshow(title, season, episode, year, imdb_id)
	else:
		metadata = trakt.get_movie_details(imdb_id)
		year = metadata['year']
		title = metadata['title']
		resolved_url = Scraper.search_movie(title, year, imdb_id=imdb_id)
	if not resolved_url: return
	plugin.play_stream(resolved_url, metadata=metadata)
plugin.register('watch_stream', watch_stream)


if __name__ == '__main__':
	plugin.run()
