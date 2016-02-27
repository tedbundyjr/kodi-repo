from dudehere.routines import *
if ADDON.get_bool_setting('movie_custom_directory'):
	MOVIE_DIRECTORY = ADDON.get_setting('movie_directory')
else:
	MOVIE_DIRECTORY = "special://userdata/addon_data/%s/movies" % ADDON_ID
if ADDON.get_bool_setting('tv_show_custom_directory'):
	TVSHOW_DIRECTORY = ADDON.get_setting('tv_show_directory')
else:
	TVSHOW_DIRECTORY = "special://userdata/addon_data/%s/tvshows" % ADDON_ID

if ADDON.get_setting('database_type')=='1':
	DB_NAME = ADDON.get_setting('database_mysql_name')
	DB_USER = ADDON.get_setting('database_mysql_user')
	DB_PASS = ADDON.get_setting('database_mysql_pass')
	DB_PORT = ADDON.get_setting('database_mysql_port')
	DB_ADDRESS = ADDON.get_setting('database_mysql_host')
	DB_TYPE = 'mysql'

else:
	DB_TYPE = 'sqlite'
	DB_FILE = xbmc.translatePath(ADDON.get_setting('database_sqlite_file'))

WATCH_PERCENT		= 94

WATCHLIST_COLOR 	= ADDON.get_setting('custom_color_watchlist')
SYNC_COLOR			= ADDON.get_setting('custom_color_sync')
DISABLED_COLOR		= ADDON.get_setting('custom_color_disabled')
ENABLED_COLOR		= ADDON.get_setting('custom_color_enabled')
NEXTPAGE_COLOR		= ADDON.get_setting('custom_color_nextpage')
PREVIOUSPAGE_COLOR		= ADDON.get_setting('custom_color_previouspage')

if ADDON.get_setting('enable_default_views') == 'true':
	VIEWS = enum(DEFAULT=ADDON.get_setting('default_folder_view'), LIST=50, BIGLIST=51, THUMBNAIL=500, SMALLTHUMBNAIL=522, FANART=508, POSTERWRAP=501, MEDIAINFO=504, MEDIAINFO2=503, MEDIAINFO3=515, WIDE=505, LIST_DEFAULT=ADDON.get_setting('default_list_view'), TV_DEFAULT=ADDON.get_setting('default_tv_view'), MOVIE_DEFAULT=ADDON.get_setting('default_movie_view'), SEASON_DEFAULT=ADDON.get_setting('default_season_view'), EPISODE_DEFAULT=ADDON.get_setting('default_episode_view'))