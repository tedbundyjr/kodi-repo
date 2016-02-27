from dudehere.routines import *
from dudehere.routines.i18nlib import i18n
class STRINGS():
	def map(self, key):
		table = {
			'tv_menu': 					30000,
			'movie_menu': 				30001,
			'set_language': 			30002,
			'quick_search':				30003,
			'settings_menu': 			30004,
			'transmogrified':			30005,
			'update_now':	 			30006,
			'show_help': 				30007,
			'tv_calendar': 				30008,
			'watchlist': 				30009,
			'custom_lists': 			30010,
			'genres': 					30011,
			'tv_recommended': 			30012,
			'tv_popular':				30013,
			'tv_trending':				30014,
			'search':					30015,
			'movie_recommended':		30016,
			'movie_popular':			30017,
			'movie_trending':			30018,
			'add_source_folders':		30019,
			'manage_subscriptions':		30020,
			'manage_hostlist':			30021,
			'alluc_settings':			30022,
			'transmogrifier_settings':	30023,
			'urlresolver_settings':		30024,
			'reset_alluc':				30025,
			'tv_transmogrified':		30026,
			'movie_transmogrified':		30027,
			'transmogrifier_queue':		30028,
			'authorize_trakt':			30029,
			'enable_basic_mode':		30030,
			'enable_advanced_mode':		30031,
			'advanced_search':			30052,
			'my_favorites':				30100
		}
		
		if key in table.keys():
			return i18n(table[key])
		else:
			return False