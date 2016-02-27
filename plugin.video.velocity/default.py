# -*- coding: utf-8 -*-
#
#Velocity by Blazetamer   2015
  
from urllib2 import Request, urlopen
import urllib2,urllib,re,os
import sys
import urlresolver
import xbmcplugin,xbmcgui,xbmc, xbmcaddon, downloader, extract, time
import tools
from libs import kodi,trakt_auth,trakt,trakt_auth
from tm_libs import dom_parser
from libs import log_utils,message
from libs import window_box


from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from scrapers import main_scrape ,primewire,twomovies,zmovies,merdb,iwatchonline,nine_movies
import cookielib


ADDON = xbmcaddon.Addon(id=kodi.addon_id)
net = Net()
addon_id=kodi.addon_id
addon = Addon(addon_id, sys.argv)
artwork = xbmc.translatePath(os.path.join('special://home','addons',addon_id,'resources','art/'))
fanart = artwork+'fanart.jpg'
messages = xbmc.translatePath(os.path.join('special://home','addons',addon_id,'resources','messages/'))
execute = xbmc.executebuiltin
trakt_api=trakt.TraktAPI()

def LogNotify(title,message,times,icon):
		xbmc.executebuiltin("XBMC.Notification("+title+","+message+","+times+","+icon+")")


def OPEN_URL(url):
	req=urllib2.Request(url)
	req.add_header('User-Agent', 'Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; AFTB Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30')
	response=urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link


def menu():

	kodi.addDir("Movies",'','movie_menu',artwork+'movies.png','',1,'','',fanart=fanart)
	kodi.addDir("TV Shows",'','tv_menu',artwork+'tvshows.png','',1,'','',fanart=fanart)
	kodi.addDir("General Settings",'','display_settings',artwork+'gen_settings.png','',1,'','',fanart=fanart)
	kodi.addDir("Scraper Settings",'','display_scraper_settings',artwork+'scraper_settings.png','',1,'','',fanart=fanart)
	kodi.addDir("Trakt Settings",'','display_trakt_settings',artwork+'trakt_settings.png','',1,'','',fanart=fanart)
	kodi.addDir("Set Download Folder",'','display_download_settings',artwork+'down_settings.png','',1,'','',fanart=fanart)
	if not kodi.get_setting('trakt_oauth_token'):
			kodi.addDir("[COLOR gold]Trakt Intergration(Some remotes will need to use settings menu)[/COLOR]",messages+'trakt_auth.txt','window_box',artwork+'trakt.png','',1,'','',fanart=fanart,is_playable=False,is_folder=True)
	kodi.auto_view('list')


def movie_menu():

		kodi.addDir("Popular",'popular','call_trakt_movies',artwork+'popular.png','',1,'','',fanart=fanart)
		kodi.addDir("Trending",'trending','call_trakt_movies',artwork+'trending.png','',1,'','',fanart=fanart)
		kodi.addDir("Most Watched",'most_watched','call_trakt_movies',artwork+'most_watched.png','',1,'','',fanart=fanart)
		kodi.addDir("Most Played",'most_played','call_trakt_movies',artwork+'most_played.png','',1,'','',fanart=fanart)
		kodi.addDir("Most Collected",'most_collected','call_trakt_movies',artwork+'most_collected.png','',1,'','',fanart=fanart)
		kodi.addDir("Box Office",'box_office','call_trakt_movies',artwork+'box_office.png','',1,'','',fanart=fanart)
		kodi.addDir("Search",'','trakt_search_movies',artwork+'search.png','',1,'','',fanart=fanart)
		if kodi.get_setting('trakt_oauth_token'):
			#kodi.addDir("Refresh my Trakt Login [COLOR red](ONLY if below sections fail)[/COLOR]",'','get_token',artwork+'refresh.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]My Movie Collection[/COLOR]",'my_collected','call_trakt_movies',artwork+'my_collection.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Recomended for me[/COLOR]",'my_recomends','call_trakt_movies',artwork+'recomended.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Movie Watchlist[/COLOR]",'get_watchlist_movies','call_trakt_movies',artwork+'watchlist.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Watched Movie History[/COLOR]",'get_watched_history','call_trakt_movies',artwork+'watchhistory.png','',1,'','',fanart=fanart)
		kodi.auto_view('list')


def tv_menu():
	kodi.addDir("Popular TV",'popular_tv','call_trakt_tv',artwork+'popular_tv.png','',1,'','',fanart=fanart)
	kodi.addDir("Trending TV",'trending_tv','call_trakt_tv',artwork+'trending_tv.png','',1,'','',fanart=fanart)
	kodi.addDir("Most Watched TV",'most_watched_tv','call_trakt_tv',artwork+'most_watched_tv.png','',1,'','',fanart=fanart)
	kodi.addDir("Most Played TV",'most_played_tv','call_trakt_tv',artwork+'most_played_tv.png','',1,'','',fanart=fanart)
	kodi.addDir("Most Collected TV",'most_collected_tv','call_trakt_tv',artwork+'most_collected_tv.png','',1,'','',fanart=fanart)
	kodi.addDir("Search",'','trakt_search_shows',artwork+'search.png','',1,'','',fanart=fanart)
	if kodi.get_setting('trakt_oauth_token'):
			#kodi.addDir("Refresh my Trakt Login [COLOR red](ONLY if below sections fail)[/COLOR]",'','get_token',artwork+'refresh.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Collected Episodes Not Watched[/COLOR]",'need_to_watch','call_trakt_tv',artwork+'tv_watchlist.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Collected TV Shows[/COLOR]",'my_collected_tvshows','call_trakt_tv',artwork+'my_tv_collection.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Recomended TV Shows for me[/COLOR]",'my_recomends_tvshows','call_trakt_tv',artwork+'tv_recomended.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]TV Shows Watchlist [/COLOR]",'get_watchlist_tvshows','call_trakt_tv',artwork+'my_tv_watchlist.png','',1,'','',fanart=fanart)
			#kodi.addDir("[COLOR gold]TV Shows Calendar[/COLOR]",'get_shows_calendar','call_trakt_tv',artwork+'watchlist.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Anticipated TV Shows[/COLOR]",'get_anticipated_tvshows','call_trakt_tv',artwork+'tv_antic.png','',1,'','',fanart=fanart)
			kodi.addDir("[COLOR gold]Watched TV History[/COLOR]",'get_watched_history','call_trakt_tv',artwork+'tv_watchhistory.png','',1,'','',fanart=fanart)
	kodi.auto_view('list')

def call_trakt_tv(url):
	try:
		#Auth TV SHOWS
		media = 'shows'
		if url == 'get_watched_history':
			links = trakt_api.get_watched_history(media)
			for e in links:
				Labels = trakt_api.get_show_details(e)
				infoLabels=trakt_api.process_show(Labels)
				menu_items=[]
				trakt_id = str(infoLabels['trakt_id'])
				trailer = infoLabels['trailer_url']
				year = str(infoLabels['year'])
				name = infoLabels['title'].encode('utf-8')
				thumb=infoLabels['cover_url']
				if thumb is None:
					thumb = ''
				menu_items=[]
				menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Add as Watched[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watched_history', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Find Similar Shows[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'similar_shows', 'name':name})))
				menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
				if url == 'get_watchlist_tvshows':
					menu_items.append(('[COLOR gold]Remove From Want to Watch[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_watchlist', 'name':name, 'media':media})))
				else:
					menu_items.append(('[COLOR gold]Add to Want To Watch[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))
				if trailer:
					utube = tools.make_trailer(trailer)
					menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
				kodi.addDir(name+' ('+year+')','','find_season',thumb,name,5,trakt_id,'shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=False)
				kodi.auto_view('tvshows')

		else:
			if url == 'need_to_watch':
				#link = trakt_api.get_watchlist_tvshows()
				#link = trakt_api.get_calendar_shows()
				link = trakt_api.get_my_collected_tvshows()#*** THIS ALMOST WORKS
				#link = trakt_api.get_watched_history('shows')
				#link = trakt_api.get_calendar_episodes()
				#link = trakt_api.get_calendar_daily_shows()
				for e in link:
					infoLabels = trakt_api.process_show(e)
					show_trakt_id = str(infoLabels['trakt_id'])
					show_year = str(infoLabels['year'])
					show_name = infoLabels['title'].encode('utf-8')
					orig_name = show_name+' ('+show_year+')'
					link = trakt_api.get_show_progress(show_trakt_id)
					if link['next_episode'] is not None:
						epi = link['next_episode']
						title = epi['title'].encode('utf-8')
						season = epi['season']
						episode = epi['number']
						trakt = epi['ids']
						trakt_id = trakt['trakt']
						infoLabels = trakt_api.get_episode_details(show_trakt_id,season,episode)
						aired = infoLabels['premiered']
						# print aired
						# print infoLabels

						menu_items=[]
						trailer = infoLabels['trailer_url']
						year = str(infoLabels['year'])
						name = infoLabels['title'].encode('utf-8')
						if name == 'TBA':
							name = '[COLORred]'+name+'[/COLOR]'
						else:
							name = '[COLORgreen]'+name+'[/COLOR]'

						thumb=infoLabels['cover_url']
						if thumb is None:
							thumb = ''
						if 'null' in trailer or trailer == '':
							menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
							menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
							menu_items.append(('[COLOR gold]Add to Watched History[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watched_episode', 'name':name, 'media':media})))
						else:
							utube = tools.make_trailer(trailer)
							menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
							menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
							menu_items.append(('[COLOR gold]Add to Watched History[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watched_episode', 'name':name, 'media':media})))
							menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
						kodi.addDir('S'+str(season)+'E'+str(episode)+'  '+orig_name+' / '+name,'','findsource',thumb,orig_name,5,'','shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=True)
						kodi.auto_view('tvshows')
			else:
				if url == 'get_anticipated_tvshows':
					link = trakt_api.get_anticipated_tvshows()
				if url == 'get_shows_calendar':
					link = trakt_api.get_calendar_shows()
				if url == 'get_watchlist_tvshows':
					link = trakt_api.get_watchlist_tvshows()
				if url == 'my_recomends_tvshows':
					link = trakt_api.get_recommended_tvshows()
				if url == 'my_collected_tvshows':
					link = trakt_api.get_my_collected_tvshows()

				#TV STANDARD LISTS
				if url =='popular_tv':
					link = trakt_api.get_popular_tvshows()
				if url == 'trending_tv':
					link = trakt_api.get_trending_tvshows()
				if url == 'most_watched_tv':
					link = trakt_api.get_most_watched_tvshows()
				if url == 'most_played_tv':
					link = trakt_api.get_most_played_tvshows()
				if url == 'most_collected_tv':
					link = trakt_api.get_most_collected_tvshows()

				for e in link:

						infoLabels = trakt_api.process_show(e)
						trailer = infoLabels['trailer_url']
						trakt_id = str(infoLabels['trakt_id'])
						imdb = str(infoLabels['imdb_id'])
						year = str(infoLabels['year'])
						name = infoLabels['title'].encode('utf-8')
						thumb=infoLabels['cover_url']
						if thumb is None:
							thumb = ''
							# TODO FIX REFRESH
						menu_items=[]
						#menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
						menu_items.append(('[COLOR gold]Add to Watched History[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watched_history', 'name':name, 'media':media})))
						menu_items.append(('[COLOR gold]Find Similar Shows[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'similar_shows', 'name':name})))
						menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
						if url == 'my_collected_tvshows':
							menu_items.append(('[COLOR gold]Remove From Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_collection', 'name':name, 'media':media})))
						else: menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
						if url == 'get_watchlist_tvshows':
							menu_items.append(('[COLOR gold]Remove From Watchlist[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_watchlist', 'name':name, 'media':media})))
						else:
							menu_items.append(('[COLOR gold]Add to Watchlist[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))
						if trailer:
							utube = tools.make_trailer(trailer)
							menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
						kodi.addDir(name+' ('+year+')','','find_season',thumb,name,5,trakt_id,'shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=False)
						kodi.auto_view('tvshows')
	except Exception as e:
			log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
			LogNotify('ERROR LOGGED','%s  %s' % (str(e), 'Continuing if Possible'),'10000','')



def find_season(name,trakt_id):

	try:
		movie_title =name
		link = trakt_api.get_show_seasons(trakt_id)
		for e in link:
					infoLabels = trakt_api.process_show(e)
					menu_items=[]
					kodi.addDir('Season '+str(infoLabels['number']),'','find_episode',infoLabels['cover_url'],movie_title,5,trakt_id,'shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=True)
					kodi.auto_view('season')
	except Exception as e:
            log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
            if kodi.get_setting('error_notify') == "true":
                kodi.notify(header='Seasons',msg='(error) %s  %s' % (str(e), ''),duration=5000,sound=None)


def find_episode(name,trakt_id,movie_title):

	try:
		season = name.replace('Season ','')
		link = trakt_api.get_show_episodes(trakt_id,season)
		for e in link:
					seaLabels = trakt_api.process_episode(e)
					episode = seaLabels['episode']
					infoLabels = trakt_api.get_episode_details(trakt_id,season,episode)
					menu_items=[]
					trailer = infoLabels['trailer_url']
					year = str(infoLabels['year'])
					name = infoLabels['title'].encode('utf-8')
					thumb=infoLabels['cover_url']
					if thumb is None:
						thumb = ''
					if 'null' in trailer or trailer == '':
						menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
					else:
						utube = tools.make_trailer(trailer)
						menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
						menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
					kodi.addDir('S'+str(season)+'E'+str(episode)+'  '+name,'','findsource',thumb,movie_title,5,'','shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=True)
					kodi.auto_view('episode')
	except Exception as e:
            log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
            if kodi.get_setting('error_notify') == "true":
                kodi.notify(header='Episodes',msg='(error) %s  %s' % (str(e), ''),duration=5000,sound=None)






# TODO FIX MENU LISTING
def similar_shows(trakt_id):

	media = 'shows'
	link =trakt_api.get_similar_tvshows(trakt_id)
	for e in link:
				infoLabels = trakt_api.process_show(e)
				menu_items=[]
				trailer = infoLabels['trailer_url']
				trakt_id = str(infoLabels['trakt_id'])
				imdb = str(infoLabels['imdb_id'])
				year = str(infoLabels['year'])
				name = infoLabels['title'].encode('utf-8')
				thumb=infoLabels['cover_url']
				if thumb is None:
					thumb = ''
				menu_items=[]
				menu_items.append(('[COLOR gold]Find Similar Shows[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'similar_shows', 'name':name})))
				menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
				if url == 'get_watchlist_tvshows':
					menu_items.append(('[COLOR gold]Remove From Watchlist[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_watchlist', 'name':name, 'media':media})))
				else:
					menu_items.append(('[COLOR gold]Add to Watchlist[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))
				if trailer:
					utube = tools.make_trailer(trailer)
					menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
				kodi.addDir(name+' ('+year+')','','find_season',thumb,name,5,trakt_id,'shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=False)
				kodi.auto_view('tvshows')

def call_trakt_movies(url):

	try:
		media = 'movies'
		#MOVIE Auth Lists
		if url == 'get_watched_history':
			links = trakt_api.get_watched_history('movies')
			traktid = links['trakt']
			for trakt_id in traktid:
				infoLabels =trakt_api.get_movie_details(trakt_id)
				menu_items=[]
				trakt_id = str(infoLabels['trakt_id'])
				trailer = infoLabels['trailer_url']
				year = str(infoLabels['year'])
				name = infoLabels['title'].encode('utf-8')
				thumb=infoLabels['cover_url']
				if thumb is None:
					thumb = ''
				if 'null' in trailer or trailer == '':
					menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
				else:
					utube = tools.make_trailer(trailer)
					menu_items.append(('[COLOR gold]Remove from Watched History[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'del_watched_history', 'name':name, 'media':media})))
					menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
					menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
					menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
				kodi.addDir(name+' ('+year+')','','findsource',thumb,name,5,'','movies',meta_data=infoLabels,menu_items=menu_items,replace_menu=True)
				kodi.auto_view('movies')
		else:

			if url == 'get_watchlist_movies':
				link = trakt_api.get_watchlist_movies()
			if url == 'my_recomends':
				link = trakt_api.get_recommended_movies()
			if url == 'my_collected':
				link = trakt_api.get_my_collected()

			#MOVIE Standard Lists
			if url == 'trending':
				link = trakt_api.get_trending_movies()
			if url =='popular':
				link = trakt_api.get_popular_movies()
			if url == 'most_watched':
				link = trakt_api.get_most_watched_movies()
			if url == 'most_played':
				link = trakt_api.get_most_played_movies()
			if url == 'most_collected':
				link = trakt_api.get_most_collected_movies()
			if url == 'box_office':
				link = trakt_api.get_boxoffice_movies()
			for e in link:
				#print e
				infoLabels = trakt_api.process_movie(e)
				menu_items=[]
				trakt_id = str(infoLabels['trakt_id'])
				trailer = infoLabels['trailer_url']
				year = str(infoLabels['year'])
				name = infoLabels['title'].encode('utf-8')
				thumb=infoLabels['cover_url']
				if thumb is None:
					thumb = ''
				if url == 'my_collected':
					menu_items.append(('[COLOR gold]Remove From Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_collection', 'name':name, 'media':media})))
				else:
					menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Add to Watched History[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watched_history', 'name':name, 'media':media})))
				if url == 'get_watchlist_movies':
						menu_items.append(('[COLOR gold]Remove From Watchlist[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_watchlist', 'name':name, 'media':media})))
				else:
						menu_items.append(('[COLOR gold]Add to Watchlist[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
				if trailer:
					utube = tools.make_trailer(trailer)
					menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))


				kodi.addDir(name+' ('+year+')','','findsource',thumb,name,5,'','movies',meta_data=infoLabels,menu_items=menu_items,replace_menu=False)
				kodi.auto_view('movies')
	except Exception as e:
			#print e
			log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
			LogNotify('ERROR LOGGED','%s  %s' % (str(e), 'Continuing if Possible'),'10000','')



def add_collection(media,trakt_id):
	print "MEDIA IS = "+media
	trakt_api.add_to_collection(media, trakt_id)
	kodi.LogNotify('TRAKT ','The item has been added','3000','')
	#return

def remove_collection(media,trakt_id):
	print "MEDIA IS = "+media
	trakt_api.remove_from_collection(media, trakt_id)
	kodi.LogNotify('TRAKT ','The item has been removed','3000','')
	#return

def add_watchlist(media,trakt_id):
	link =trakt_api.add_to_watchlist(media,trakt_id)
	kodi.LogNotify('TRAKT ','The item has been added','3000','')
# 	TODO Add Notificatiopn of success



def remove_watchlist(media,trakt_id):
	link =trakt_api.delete_from_watchlist(media,trakt_id)
	kodi.LogNotify('TRAKT ','The item has been removed','3000','')
# 	TODO Add Notificatiopn of success


def add_watched_history(media,trakt_id,season=None):
	print "MEDIA IS = "+media
	trakt_api.set_watched_state(media, trakt_id, watched=True, season=None)
	#return

def del_watched_history(media,trakt_id,season=None):
	trakt_api.set_watched_state(media, trakt_id, watched=False, season=None)
	#return

def add_watched_episode(media,trakt_id,season=None):
	print "MEDIA IS = "+media
	print "SEASON IS = "+media
	trakt_api.set_watched_state('episode', trakt_id, watched=True, season=None)
	#return


#Start Ketboard Function
def _get_keyboard( default="", heading="", hidden=False ):
	keyboard = xbmc.Keyboard( default, heading, hidden )
	keyboard.doModal()
	if ( keyboard.isConfirmed() ):
		return unicode( keyboard.getText(), "utf-8" )
	return default


def pininput():
	vq = _get_keyboard( heading="Enter Pin# found at http://trakt.tv/pin/7558" )
	if ( not vq ): return False, 0
	title = urllib.quote_plus(vq)
	trakt_api._authorize(pin=title)
	#trakt_auth.get_token(pin=title)


def otherinput():
	vq = _get_keyboard( heading="Enter Your Query" )
	if ( not vq ): return False, 0
	title = urllib.quote_plus(vq)
	trakt_auth.get_token(pin=title)


#Start Search Function
def trakt_search_movies(url):
	media = 'movies'
	vq = _get_keyboard( heading="Searching for Movies" )
	if ( not vq ): return False, 0
	title = urllib.quote_plus(vq)
	link = trakt_api.search_movies(title)
	for e in link:
			#print e
			infoLabels = trakt_api.process_movie(e)
			trakt_id = str(infoLabels['trakt_id'])
			trailer = str(infoLabels['trailer_url'])
			year = str(infoLabels['year'])
			name = infoLabels['title'].encode('utf-8')
			thumb=infoLabels['cover_url']
			if thumb is None:
				thumb = ''
			menu_items=[]
			if 'null' in trailer or trailer == '':
				menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
				menu_items.append(('[COLOR gold]Add to Watchlist[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))

			else:

				utube = tools.make_trailer(trailer)
				if url == 'get_watchlist_movies':
					menu_items.append(('[COLOR gold]Remove From Watchlist[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_watchlist', 'name':name, 'media':media})))
				else:
					menu_items.append(('[COLOR gold]Add to Watchlist[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
				menu_items.append(('[COLOR gold]Add to Collection[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_collection', 'name':name, 'media':media})))
				menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
			kodi.addDir(name+' ('+year+')','','findsource',thumb,name,5,trakt_id,media,meta_data=infoLabels,menu_items=menu_items,replace_menu=True)
			kodi.auto_view('movies')


def trakt_search_shows(url):
	media = 'shows'
	vq = _get_keyboard( heading="Searching for Shows" )
	if ( not vq ): return False, 0
	title = urllib.quote_plus(vq)
	link = trakt_api.search_tv(title)
	for e in link:

					infoLabels = trakt_api.process_show(e)
					trailer = infoLabels['trailer_url']
					trakt_id = str(infoLabels['trakt_id'])
					imdb = str(infoLabels['imdb_id'])
					year = str(infoLabels['year'])
					name = infoLabels['title'].encode('utf-8')
					thumb=infoLabels['cover_url']
					if thumb is None:
						thumb = ''
						# TODO FIX REFRESH
					menu_items=[]
					menu_items.append(('[COLOR gold]Add to Watched History[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watched_history', 'name':name, 'media':media})))
					menu_items.append(('[COLOR gold]Find Similar Shows[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'similar_shows', 'name':name})))
					menu_items.append(('[COLOR gold]Show Information[/COLOR]', 'XBMC.Action(Info)'))
					if url == 'get_watchlist_tvshows':
						menu_items.append(('[COLOR gold]Remove From Watchlist[/COLOR]', 'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'remove_watchlist', 'name':name, 'media':media})))
					else:
						menu_items.append(('[COLOR gold]Add to Watchlist[/COLOR]',      'XBMC.Container.Update(%s)' % addon.build_plugin_url({'trakt_id':trakt_id, 'mode':'add_watchlist', 'name':name, 'media':media})))
					if trailer:
						utube = tools.make_trailer(trailer)
						menu_items.append(('[COLOR gold]Play Trailer[/COLOR]', 'PlayMedia('+utube+',xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image))'))
					kodi.addDir(name+' ('+year+')','','find_season',thumb,name,5,trakt_id,'shows',meta_data=infoLabels,menu_items=menu_items,replace_menu=False)
					kodi.auto_view('tvshows')


def get_params():
		param=[]
		paramstring=sys.argv[2]
		if len(paramstring)>=2:
				params=sys.argv[2]
				cleanedparams=params.replace('?','')
				if (params[len(params)-1]=='/'):
						params=params[0:len(params)-2]
				pairsofparams=cleanedparams.split('&')
				param={}
				for i in range(len(pairsofparams)):
						splitparams={}
						splitparams=pairsofparams[i].split('=')
						if (len(splitparams))==2:
								param[splitparams[0]]=splitparams[1]

		return param


params=get_params()

url=None
name=None
mode=None
trakt_id=None
thumb = None


try:
		iconimage=urllib.unquote_plus(params["iconimage"])
except:
		pass

try:
		thumb=urllib.unquote_plus(params["thumb"])
except:
		pass

try:
		fanart=urllib.unquote_plus(params["fanart"])
except:
		pass
try:
		description=urllib.unquote_plus(params["description"])
except:
		pass

try:
		filetype=urllib.unquote_plus(params["filetype"])
except:
		pass

# END OF HelpSection addition ===========================================

try:
		url=urllib.unquote_plus(params["url"])
except:
		pass

try:
		media=urllib.unquote_plus(params["media"])
except:
		pass

try:
		name=urllib.unquote_plus(params["name"])
except:
		pass
try:
		mode=urllib.unquote_plus(params["mode"])
except:
		pass

try:
		year=urllib.unquote_plus(params["year"])
except:
		pass

try:
		imdb_id=urllib.unquote_plus(params["imdb_id"])
except:
		pass

try:
		movie_title=urllib.unquote_plus(params["movie_title"])
except:
		pass


try:
		trakt_id=urllib.unquote_plus(params["trakt_id"])
except:
		pass



if kodi.get_setting('debug') == "true":
	print "Mode: "+str(mode)
	print "URL: "+str(url)
	print "Name: "+str(name)
	print "Thumb: "+str(thumb)


if mode==None :
		menu()

elif mode=='call_trakt_movies':
		call_trakt_movies(url)

elif mode=='call_trakt_tv':
		call_trakt_tv(url)

elif mode=='movie_menu':
		movie_menu()

elif mode=='tv_menu':
		tv_menu()

elif mode=='similar_shows':
		similar_shows(trakt_id)

elif mode=='add_watchlist':
		add_watchlist(media,trakt_id)

elif mode=='add_collection':
		add_collection(media,trakt_id)

elif mode=='remove_collection':
		remove_collection(media,trakt_id)

elif mode=='add_watched_history':
		add_watched_history(media,trakt_id)

elif mode=='add_watched_episode':
		add_watched_episode(media,trakt_id)

elif mode=='del_watched_history':
		del_watched_history(media,trakt_id)

elif mode=='remove_watchlist':
		remove_watchlist(media,trakt_id)

elif mode=='trakt_search_movies':
		trakt_search_movies(url)

elif mode=='trakt_search_shows':
		trakt_search_shows(url)

elif mode=='tmovies':
		twomovies.tmovies(name)

elif mode=='tmlinkpage':
		twomovies.tmlinkpage(url,movie_title,thumb,media)

elif mode=='playmerdblink':
		merdb.playmerdblink(url,movie_title,thumb)

elif mode=='playiwatchonlink':
		iwatchonline.playiwatchonlink(url,movie_title,thumb)

elif mode=='playzmovieslink':
		zmovies.playzmovieslink(url,movie_title,thumb)

elif mode=='playprimelink':
		primewire.playprimelink(url,movie_title,thumb)  #########MAY REMOVE###########

elif mode=='get_link':
		main_scrape.get_link(url,movie_title,thumb,media)

elif mode=='get_tv_link':
		main_scrape.get_tv_link(url,movie_title,thumb,media)

elif mode=='findsource':
		main_scrape.find_source(name,thumb,media,movie_title)

elif mode=='find_episode':
		find_episode(name,trakt_id,movie_title)

elif mode=='find_season':
		find_season(name,trakt_id)

elif mode=='get_token':
		trakt_api=trakt.TraktAPI()
		trakt_api._authorize()

elif mode=='pininput':
		pininput()

elif mode=='message_stat':
		message.message_stat(url)

elif mode=='window_box':
		window_box.run_box()

elif mode=='playlink':
		main_scrape.playlink()




#Settings Openings
elif mode=='display_settings':
		kodi.openSettings(addon_id,id1=9,id2=0)

elif mode=='display_download_settings':
		kodi.openSettings(addon_id,id1=9,id2=1)

elif mode=='display_trakt_settings':
		kodi.openSettings(addon_id,id1=9,id2=2)

elif mode=='display_scraper_settings':
		kodi.openSettings(addon_id,id1=9,id2=3)

xbmcplugin.endOfDirectory(int(sys.argv[1]))



# TODO  PutMV and 9Movies
'''
http://miradetodo.com.ar/videos/
http://movie.pubfilmno1.com
http://xmovies8.tv
http://www.izlemeyedeger.com
http://tunemovie.is
http://cyberreel.com
http://123movies.to
'''

'''
.decode('utf-8')
'''