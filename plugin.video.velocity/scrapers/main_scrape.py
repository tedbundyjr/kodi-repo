import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmc
import xbmcvfs
import urllib
import urlparse
import sys
import os
import re
import urlresolver
import time
from threading import Thread
from Queue import Queue


import twomovies, merdb,iwatchonline,zmovies,primewire,afdah,nine_movies
from libs import kodi,trakt_auth
from libs import log_utils
from t0mm0.common.addon import Addon


ADDON = xbmcaddon.Addon(id=kodi.addon_id)
addon_id=kodi.addon_id
addon = Addon(addon_id, sys.argv)

MAX_ERRORS = 10

def wrapper(func, arg, queue):
    queue.put(func(arg))

def find_source(name,thumb,media,movie_title):
    q1, q2, q3, q4, q5, q6, q7, q8 = Queue(), Queue(), Queue(),Queue(), Queue(), Queue(), Queue(), Queue()
    try:
        if thumb is None:
            thumb = ''
        else:
            thumb = thumb
        if media == 'shows':
            find_sourceTV(name,thumb,media,movie_title)
        else:
            if kodi.get_setting('9movies') == "true":
                movie_title = name
                t = Thread(target=wrapper, args=(nine_movies.ninemovies, name, q1))
                t.daemon = True
                #Thread(target=wrapper, args=(nine_movies.ninemovies, name, q1)).start()
                t.start()
                #t.join(int(scraper_timeout))

            if kodi.get_setting('primewire') == "true":
                movie_title = name
                Thread(target=wrapper, args=(primewire.primewire, name, q2)).start()

            if kodi.get_setting('twomovies') == "true":
                movie_title = name
                Thread(target=wrapper, args=(twomovies.tmovies, name, q3)).start()

            if kodi.get_setting('afdah') =='true':
                movie_title = name
                Thread(target=wrapper, args=(afdah.afdah, name, q4)).start()

            if kodi.get_setting('merdb') == "true":
                movie_title = name
                Thread(target=wrapper, args=(merdb.merdb, name, q5)).start()

            if kodi.get_setting('zmovies') == "true":
                movie_title = name
                Thread(target=wrapper, args=(zmovies.zmovies, name, q6)).start()

            if kodi.get_setting('9movies') == "true":
                ninesources = q1.get()
                for e in ninesources:
                    total_items =len(ninesources)
                    names = e['linkname']
                    urls = e['url']
                    views = e['view']
                    quals = e['quality']
                    kodi.addDir("[COLORteal][9Movies][/COLOR] - "+names+' ['+quals+']',urls,'get_link',thumb,movie_title,total_items,'','movies')

            if kodi.get_setting('primewire') == "true":
                primesources = q2.get()
                for e in primesources:
                    total_items =len(primesources)
                    names = e['linkname']
                    urls = e['url']
                    views = e['view']
                    quals = e['quality']
                    kodi.addDir("[COLORblue][Primewire][/COLOR] - "+names+' ['+quals+']'+' Views '+views,urls,'get_link',thumb,movie_title,total_items,'','movies')

            if kodi.get_setting('twomovies') == "true":
                tmsources = q3.get()
                for e in tmsources:
                    total_items =len(tmsources)
                    names = e['linkname']
                    urls = e['url']
                    kodi.addDir("[COLORgold][Two Movies][/COLOR] - "+names,urls,'tmlinkpage',thumb,movie_title,total_items,'','movies')

            if kodi.get_setting('afdah') =='true':
                afdahsources = q4.get()
                for e in afdahsources:
                        total_items =len(afdahsources)
                        names = e['linkname']
                        urls = e['url']
                        quals = e['quality']
                        kodi.addDir("[COLORgreen][AFDAH][/COLOR] - "+names+' ['+quals+']',urls,'get_link',thumb,movie_title,total_items,'','movies')

            if kodi.get_setting('merdb') == "true":
                mersources = q5.get()
                for e in mersources:
                    total_items =len(mersources)
                    names = e['linkname']
                    urls = e['url']
                    kodi.addDir("[MerDB] - "+names,urls,'playmerdblink',thumb,movie_title,total_items,'','movies')

            if kodi.get_setting('zmovies') == "true":
                zmoviesources =q6.get()
                for e in zmoviesources:
                    total_items =len(zmoviesources)
                    names = e['linkname']
                    urls = e['url']
                    kodi.addDir("[ZMovies] - "+names,urls,'playzmovieslink',thumb,movie_title,total_items,'','movies')
    except Exception as e:
            log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
            if kodi.get_setting('error_notify') == "true":
                kodi.notify(header='Scraper',msg='(error) %s  %s' % (str(e), ''),duration=5000,sound=None)




def tv_wrapper(func, arg,arg2, queue):
    queue.put(func(arg,arg2))


def find_sourceTV(name,thumb,media,movie_title):
    q1, q2, q3, q4, q5, q6, q7, q8 = Queue(), Queue(), Queue(),Queue(), Queue(), Queue(), Queue(), Queue()
    try:
        if thumb is None:
            thumb = ''
        else:
            thumb = thumb

        if kodi.get_setting('primewire') == "true":
                Thread(target=tv_wrapper, args=(primewire.primewire_tv, name,movie_title, q2)).start()


        if kodi.get_setting('twomovies') == "true":
                Thread(target=tv_wrapper, args=(twomovies.tmovies_tv, name,movie_title, q3)).start()

        # GRAB RETURNS BELOW

        if kodi.get_setting('primewire') == "true":
                primesources = q2.get()
                for e in primesources:
                        total_items =len(primesources)
                        names = e['linkname']
                        urls = e['url']
                        views = e['view']
                        quals = e['quality']
                        kodi.addDir("[COLORblue][Primewire][/COLOR] - "+names+' ['+quals+']'+' Views '+views,urls,'get_tv_link',thumb,movie_title,total_items,'',name)
                kodi.notify(header='Primewire', msg='Search Complete', duration=2000, sound=None)

        if kodi.get_setting('twomovies') == "true":
                tmsources = q3.get()
                for e in tmsources:
                        total_items =len(tmsources)
                        names = e['linkname']
                        urls = e['url']
                        kodi.addDir("[COLORgold][TwoMovies-TV][/COLOR] - "+names,urls,'tmlinkpage',thumb,movie_title,total_items,'',name)# MUST BE EPISODE NAME IN PLACE OF MEDIA TYPE HERE
                kodi.notify(header='TwoMovies', msg='Search Complete', duration=2000, sound=None)

        # AFDAH SCRAPE
        # TODO Add TV
        if kodi.get_setting('afdah') == "true":
            print "AFDAH TV not setup yet"

        # TODO Add Mer TV Scrapers
        if kodi.get_setting('merdb') == "true":
            print "MerDb TV Not Setup Yet"


        # TODO Add ZMovies TV Scrapers
        if kodi.get_setting('zmovies') == "true":
            print "ZMovies TV Not setup yet"

    except Exception as e:
            log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
            if kodi.get_setting('error_notify') == "true":
                kodi.notify(header='Scraper',msg='(error) %s  %s' % (str(e), ''),duration=5000,sound=None)


def get_link(url,movie_title,thumb,media):
    hmf = urlresolver.HostedMediaFile(url)
    ##########################################
    if hmf:
        try:
            url = urlresolver.resolve(url)
            params = {'url':url, 'name':movie_title, 'thumb':thumb}
            addon.add_video_item(params, {'title':movie_title}, img=thumb)
            liz=xbmcgui.ListItem(movie_title, iconImage="DefaultFolder.png", thumbnailImage=thumb)
            xbmc.sleep(1000)
            xbmc.Player ().play(url, liz, False)
            movie_name = movie_title[:-6]
            movie_name = '"'+movie_name+'"'
            movie_year_full = movie_title[-6:]
            movie_year = movie_year_full.replace('(','').replace(')','')
            if kodi.get_setting('trakt_oauth_token'):
                xbmc.sleep(30000)
                print "Velocity: Movie Scrobble  Start"
                try:
                    trakt_auth.start_movie_watch(movie_name,movie_year)
                except Exception as e:
                    log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
                    if kodi.get_setting('error_notify') == "true":
                        kodi.notify(header='Scrobble not loggged', msg='%s  %s' % (str(e), ''), duration=5000, sound=None)
            xbmc.sleep(30000)
            if kodi.get_setting('trakt_oauth_token'):
                check_player(movie_name,movie_year)
        except Exception as e:
            log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
            if kodi.get_setting('error_notify') == "true":
                        kodi.notify(header='ERROR', msg='%s  %s' % (str(e), ''), duration=5000, sound=None)
    if not hmf:
        try:
            params = {'url':url, 'name':movie_title, 'thumb':thumb}
            addon.add_video_item(params, {'title':movie_title}, img=thumb)
            liz=xbmcgui.ListItem(movie_title, iconImage="DefaultFolder.png", thumbnailImage=thumb)
            xbmc.sleep(1000)
            xbmc.Player ().play(url, liz, False)
            movie_name = movie_title[:-6]
            movie_name = '"'+movie_name+'"'
            movie_year_full = movie_title[-6:]
            movie_year = movie_year_full.replace('(','').replace(')','')
            if kodi.get_setting('trakt_oauth_token'):
                xbmc.sleep(30000)
                print "Velocity: Movie Scrobble  Start"
                try:
                    trakt_auth.start_movie_watch(movie_name,movie_year)
                except Exception as e:
                    log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
                    if kodi.get_setting('error_notify') == "true":
                        kodi.notify(header='Scrobble not loggged', msg='%s  %s' % (str(e), ''), duration=5000, sound=None)

            xbmc.sleep(30000)
            if kodi.get_setting('trakt_oauth_token'):
                check_player(movie_name,movie_year)
        except Exception as e:
            log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
            if kodi.get_setting('error_notify') == "true":
                        kodi.notify(header='ERROR', msg='%s  %s' % (str(e), ''), duration=5000, sound=None)

    else:
        if kodi.get_setting('error_notify') == "true":
            kodi.notify(header='Try Another Source', msg='Link Removed or Failed', duration=4000, sound=None)
        print "Failed to play/Locate stream: "+url



def get_tv_link(url,movie_title,thumb,media):
    hmf = urlresolver.HostedMediaFile(url)
    ##########################################
    if hmf:
        url = urlresolver.resolve(url)
        params = {'url':url, 'name':media, 'thumb':thumb}
        addon.add_video_item(params, {'title':media}, img=thumb)
        liz=xbmcgui.ListItem(media, iconImage="DefaultFolder.png", thumbnailImage=thumb)
        xbmc.sleep(1000)
        xbmc.Player ().play(url, liz, False)
        movie_name = movie_title[:-6]
        movie_name = '"'+movie_name+'"'
        movie_year_full = movie_title[-6:]
        movie_year = movie_year_full.replace('(','').replace(')','')
        if kodi.get_setting('trakt_oauth_token'):
            xbmc.sleep(30000)
            print "Velocity: TV Show Scrobble  Start"
            try:
                trakt_auth.start_tv_watch(movie_name,media)
            except Exception as e:
                    log_utils.log('Error [%s]  %s' % (str(e), ''), xbmc.LOGERROR)
                    if kodi.get_setting('error_notify') == "true":
                        kodi.notify(header='Scrobble not loggged', msg='%s  %s' % (str(e), ''), duration=5000, sound=None)
        xbmc.sleep(30000)
        if kodi.get_setting('trakt_oauth_token'):
            check_tv_player(movie_name,media)
    else:
        if kodi.get_setting('error_notify') == "true":
            kodi.notify(header='Try Another Source', msg='Link Removed or Failed', duration=4000, sound=None)
        print "Failed to play/Locate stream: "+url


class Player(xbmc.Player):
    def __init__(self):
        log_utils.log('Velocity Service: starting...')
        xbmc.Player.__init__(self)
        self.win = xbmcgui.Window(10000)
        #self.reset()

    def onPlayBackStarted(self):
        log_utils.log('Service: Playback Started')


    def onPlayBackStopped(self):
        log_utils.log('Service: Playback Stopped')
        #print" RUN A STOP COMMAND"

    def onPlayBackEnded(self):
        log_utils.log('Service: Playback Ended')

        self.onPlayBackStopped()


def check_player(name,year):

    monitor = Player()

    errors = 0
    while not xbmc.abortRequested:
        try:
            #print"CHECK ONE"
            isPlaying = monitor.isPlaying()
            if  monitor.isPlayingVideo():
                monitor._lastPos = monitor.getTime()
               # print  monitor._lastPos
            else:
                print "Velocity: Scrobble Movie End"
                trakt_auth.stop_movie_watch(name,year)
                break
        except Exception as e:
            errors += 1
            if errors >= MAX_ERRORS:
                log_utils.log('Service: Error (%s) received..(%s/%s)...Ending Service...' % (e, errors, MAX_ERRORS), log_utils.LOGERROR)
                break
            else:
                log_utils.log('Service: Error (%s) received..(%s/%s)...Continuing Service...' % (e, errors, MAX_ERRORS), log_utils.LOGERROR)
        else:
            errors = 0

        xbmc.sleep(1000)



def check_tv_player(name,media):

    monitor = Player()

    errors = 0
    while not xbmc.abortRequested:
        try:
            #print"CHECK ONE"
            isPlaying = monitor.isPlaying()
            if  monitor.isPlayingVideo():
                monitor._lastPos = monitor.getTime()
               # print  monitor._lastPos
            else:
                print "Velocity: Scrobble TV Show End"
                trakt_auth.stop_tv_watch(name,media)
                break
        except Exception as e:
            errors += 1
            if errors >= MAX_ERRORS:
                log_utils.log('Service: Error (%s) received..(%s/%s)...Ending Service...' % (e, errors, MAX_ERRORS), log_utils.LOGERROR)
                break
            else:
                log_utils.log('Service: Error (%s) received..(%s/%s)...Continuing Service...' % (e, errors, MAX_ERRORS), log_utils.LOGERROR)
        else:
            errors = 0

        xbmc.sleep(1000)


