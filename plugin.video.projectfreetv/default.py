import xbmc, xbmcgui, xbmcplugin
import urllib, urllib2
import re, string

try:
    from addon.common.addon import Addon
    from addon.common.net import Net
except:
    print 'Failed to import script.module.addon.common'
    xbmcgui.Dialog().ok("PFTV Import Failure", "Failed to import addon.common", "A component needed by PFTV is missing on your system", "Please visit www.xbmchub.com for support")

addon = Addon('plugin.video.projectfreetv', sys.argv)
net = Net()

try:
    from metahandler import metahandlers
except:
    print 'Failed to import script.module.metahandler'
    xbmcgui.Dialog().ok("PFTV Import Failure", "Failed to import Metahandlers", "A component needed by PFTV is missing on your system", "Please visit www.xbmchub.com for support")


#Common Cache
import xbmcvfs
dbg = False # Set to false if you don't want debugging

#Common Cache
try:
  import StorageServer
except:
  import storageserverdummy as StorageServer
cache = StorageServer.StorageServer('plugin.video.projectfreetv')


##### Queries ##########
play = addon.queries.get('play', '')
mode = addon.queries['mode']
video_type = addon.queries.get('video_type', '')
section = addon.queries.get('section', '')
url = addon.queries.get('url', '')
title = addon.queries.get('title', '')
name = addon.queries.get('name', '')
imdb_id = addon.queries.get('imdb_id', '')
season = addon.queries.get('season', '')
episode = addon.queries.get('episode', '')

print '-----------------Project Free TV Addon Params------------------'
print '--- Version: ' + str(addon.get_version())
print '--- Mode: ' + str(mode)
print '--- Play: ' + str(play)
print '--- URL: ' + str(url)
print '--- Video Type: ' + str(video_type)
print '--- Section: ' + str(section)
print '--- Title: ' + str(title)
print '--- Name: ' + str(name)
print '--- IMDB: ' + str(imdb_id)
print '--- Season: ' + str(season)
print '--- Episode: ' + str(episode)
print '---------------------------------------------------------------'

################### Global Constants #################################

#URLS
website_url = addon.get_setting('website_url')
if website_url == "Custom URL":
    custom_url = addon.get_setting('custom_url')
    # if custom_url.endswith("/"):
        # MainUrl = custom_url
    # else:
        # MainUrl = custom_url + "/"
    MainUrl = custom_url
else:
    MainUrl = website_url

SearchUrl = MainUrl + '/search/?q=%s&md=%s'
MoviePath = "/movies/"
MovieUrl = MainUrl + MoviePath
TVPath = "/internet/"
TVUrl = MainUrl + TVPath

#PATHS
AddonPath = addon.get_path()
IconPath = AddonPath + "/icons/"

#VARIABLES
SearchMovies = 'movies'
SearchTV = 'shows'
SearchAll = 'all'

VideoType_Movies = 'movie'
VideoType_TV = 'tvshow'
VideoType_Season = 'season'
VideoType_Episode = 'episode'


#################### Addon Settings ##################################

#Helper function to convert strings to boolean values
def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")
  
meta_setting = str2bool(addon.get_setting('use-meta'))

######################################################################

def icon_path(filename):
    return IconPath + filename
    
def get_html(page_url):
    
    if addon.get_setting('proxy_enable') == 'true':
        proxy = 'http://' + addon.get_setting('proxy') + ':' + addon.get_setting('proxy_port')
        proxy_handler = urllib2.ProxyHandler({'http': proxy})
        username = addon.get_setting('proxy_user')
        password = addon.get_setting('proxy_pass')
        if username <> '' and password <> '':
            print 'Using authenticated proxy: %s' % proxy
            password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, proxy, username, password)
            proxy_auth_handler = urllib2.ProxyBasicAuthHandler(password_mgr)
            opener = urllib2.build_opener(proxy_handler, proxy_auth_handler)
        else:
            print 'Using proxy: %s' % proxy
            opener = urllib2.build_opener(proxy_handler)
        
        urllib2.install_opener(opener)

    addon.log("Requesting URL: %s" % page_url)        
    html = net.http_GET(page_url).content
    
    import HTMLParser
    h = HTMLParser.HTMLParser()
    html = h.unescape(html)
    return html.encode('utf-8')
    
    
def Notify(typeq, box_title, message, times='', line2='', line3=''):
     if box_title == '':
          box_title='PTV Notification'
     if typeq == 'small':
          if times == '':
               times='5000'
          smallicon= icon_path('icon.png')
          addon.show_small_popup(title=box_title, msg=message, delay=int(times), image=smallicon)
     elif typeq == 'big':
          addon.show_ok_dialog(message, title=box_title)
     else:
          addon.show_ok_dialog(message, title=box_title)


def setView(content, viewType):
    
    # set content type so library shows more views and info
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if addon.get_setting('auto-view') == 'true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.get_setting(viewType) )
    
    # set sort methods - probably we don't need all of them
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )


def add_favourite():
    saved_favs = cache.get('favourites_' + video_type)
    favs = []

    #Check for and remove COLOR tags which were added to titles
    r = re.search('(.+?) \[COLOR red\]', name)
    if r:
        vidname = r.group(1)
    else:
        vidname = name
        
    if saved_favs:
        favs = eval(saved_favs)
        if favs:
            if (title, vidname, imdb_id, season, episode, url) in favs:
                Notify('small', 'Favourite Already Exists', vidname.title() + ' already exists in your PFTV favourites','')
                return

    import urlparse
    split_url = urlparse.urlsplit(url)                
    new_url = MainUrl + split_url.path
    
    favs.append((title, vidname, imdb_id, season, episode, new_url))
    cache.set('favourites_' + video_type, str(favs))
    Notify('small', 'Added to favourites', vidname.title() + ' added to your PFTV favourites','')


def remove_favourite():
    saved_favs = cache.get('favourites_' + video_type)
    if saved_favs:
        favs = eval(saved_favs)

        import urlparse
        split_url = urlparse.urlsplit(url)                
        new_url = MainUrl + split_url.path
        
        favs.remove((title, name, imdb_id, season, episode, new_url))
        cache.set('favourites_' + video_type, str(favs))
        xbmc.executebuiltin("XBMC.Container.Refresh")


def refresh_movie(vidtitle, year=''):

    metaget=metahandlers.MetaData()
    search_meta = metaget.search_movies(vidtitle)
    
    if search_meta:
        movie_list = []
        for movie in search_meta:
            movie_list.append(movie['title'] + ' (' + str(movie['year']) + ')')
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose', movie_list)
        
        if index > -1:
            new_imdb_id = search_meta[index]['imdb_id']
            new_tmdb_id = search_meta[index]['tmdb_id']       
            meta = metaget.update_meta('movie', vidtitle, imdb_id=imdb_id, new_imdb_id=new_imdb_id, new_tmdb_id=new_tmdb_id, year=year)   
            xbmc.executebuiltin("Container.Refresh")
    else:
        msg = ['No matches found']
        addon.show_ok_dialog(msg, 'Refresh Results')


def refresh_tv(vidtitle, imdb_id):

    metaget=metahandlers.MetaData()      
    show_list = metaget.get_tvdb_list(vidtitle)       
    name_list = []
    filtered_show_list = []
    for show in show_list:
        (seriesid, SeriesName, IMDB_ID) = show
        if IMDB_ID != None:
            filtered_show_list.append([seriesid, SeriesName, IMDB_ID])
            name_list.append(SeriesName)

    dialog = xbmcgui.Dialog()
    index = dialog.select('Choose', name_list)
 
    if index > -1:
        metaget.update_meta('tvshow', vidtitle, imdb_id, new_tmdb_id=filtered_show_list[index][0], new_imdb_id=filtered_show_list[index][2])
        xbmc.executebuiltin("Container.Refresh")
        Notify('small', 'Updated Metadata', filtered_show_list[index][1],'') 


def episode_refresh(vidname, imdb, season_num, episode_num):
    #refresh info for an episode   

    metaget=metahandlers.MetaData()
    metaget.update_episode_meta(vidname, imdb, season_num, episode_num)
    xbmc.executebuiltin("XBMC.Container.Refresh")


def season_refresh(vidname, imdb, season_num):

    metaget=metahandlers.MetaData()          	
    metaget.update_season(vidname, imdb, season_num)
    xbmc.executebuiltin("XBMC.Container.Refresh")


def get_metadata(video_type, vidtitle, metaget=None, vidname='', year='', imdb='', season_list=None, season_num=0, episode_num=0):
    
    if meta_setting:
        #Get Meta settings
        movie_covers = addon.get_setting('movie-covers')
        tv_banners = addon.get_setting('tv-banners')
        tv_posters = addon.get_setting('tv-posters')
        
        movie_fanart = addon.get_setting('movie-fanart')
        tv_fanart = addon.get_setting('tv-fanart')
    
        if video_type in (VideoType_Movies, VideoType_TV):
            meta = metaget.get_meta(video_type, vidtitle, year=year)
    
        if video_type == VideoType_Season:
            returnlist = True
            if not season_list:
                season_list = []
                season_list.append(season_num)
                returnlist = False
            meta = metaget.get_seasons(vidtitle, imdb, season_list)
            if not returnlist:
                meta = meta[0]
    
        if video_type == VideoType_Episode:
            meta=metaget.get_episode_meta(vidtitle, imdb, season_num, episode_num)
        
        #Check for and blank out covers if option disabled
        if video_type==VideoType_Movies and movie_covers == 'false':
            meta['cover_url'] = ''
        elif video_type==VideoType_TV and tv_banners == 'false':
            meta['cover_url'] = ''
    
        #Check for banners vs posters setting    
        if video_type == VideoType_TV and tv_banners == 'true' and tv_posters == 'false':
            meta['cover_url'] = meta['banner_url']

        #Check for and blank out fanart if option disabled
        if video_type==VideoType_Movies and movie_fanart == 'false':
            meta['backdrop_url'] = ''
        elif video_type in (VideoType_TV, VideoType_Episode) and tv_fanart == 'false':
            meta['backdrop_url'] = ''

        if not video_type == VideoType_Season:
            #Lets keep the name PFTV gives us instead of TVDB
            meta['title'] = vidname

    else:
        meta = {}
        meta['title'] = vidname
        meta['cover_url'] = ''
        meta['imdb_id'] = imdb
        meta['backdrop_url'] = ''
        meta['year'] = year
        meta['overlay'] = 0
        if video_type in (VideoType_TV, VideoType_Episode):
            meta['TVShowTitle'] = vidtitle
    
    return meta


def add_contextmenu(use_meta, video_type, link, vidtitle, vidname, favourite, watched='', imdb='', year='', season_num=0, episode_num=0):
    
    contextMenuItems = []
    contextMenuItems.append(('Info', 'XBMC.Action(Info)'))

    #Check if we are listing items in the Favourites list
    if favourite:
        contextMenuItems.append(('Delete from PFTV Favourites', 'XBMC.RunPlugin(%s)' % addon.build_plugin_url({'mode': 'del_fav', 'video_type': video_type, 'title': vidtitle, 'name':vidname, 'url':link, 'imdb_id':imdb, 'season': season_num, 'episode': episode_num})))
    else:
        contextMenuItems.append(('Add to PFTV Favourites', 'XBMC.RunPlugin(%s)' % addon.build_plugin_url({'mode': 'add_fav', 'video_type': video_type, 'title': vidtitle, 'name':vidname, 'url':link, 'imdb_id':imdb, 'season': season_num, 'episode': episode_num})))

    #Meta is turned on so enable extra context menu options
    if use_meta:
        if watched == 6:
            watched_mark = 'Mark as Watched'
        else:
            watched_mark = 'Mark as Unwatched'

        contextMenuItems.append((watched_mark, 'XBMC.RunPlugin(%s?mode=watch_mark&video_type=%s&title=%s&imdb_id=%s&season=%s&episode=%s)' % (sys.argv[0], video_type, vidtitle.decode('utf-8'), imdb, season_num, episode_num)))
        contextMenuItems.append(('Refresh Metadata', 'XBMC.RunPlugin(%s?mode=refresh_meta&video_type=%s&title=%s&year=%s&season=%s&episode=%s)' % (sys.argv[0], video_type, vidtitle.decode('utf-8'), year, season_num, episode_num)))
        
        #if video_type == VideoType_Movies:
            #contextMenuItems.append(('Search for trailer', 'XBMC.RunPlugin(%s?mode=trailer_search&vidname=%s&url=%s)' % (sys.argv[0], title, link)))                        

    return contextMenuItems


def add_video_directory(mode, video_type, link, vidtitle, vidname, metaget=None, imdb='', year='', season_num=0, totalitems=0, favourite=False):

    meta = get_metadata(video_type, vidtitle, metaget=metaget, year=year, imdb=imdb, season_num=season_num)
    contextMenuItems = add_contextmenu(meta_setting, video_type, link, vidtitle, vidname, favourite, watched=meta['overlay'], imdb=meta['imdb_id'], year=year, season_num=season_num)

    meta['title'] = vidname

    #With meta data on, set watched/unwatched values for a tv show
    if meta_setting and video_type == VideoType_TV:
        properties = {}
        episodes_unwatched = str(int(meta['episode']) - meta['playcount'])
        properties['UnWatchedEpisodes'] = episodes_unwatched
        properties['WatchedEpisodes'] = str(meta['playcount'])
    else:
        properties = None

    addon.add_directory({'mode': mode, 'url': link, 'video_type': VideoType_Season, 'imdb_id': meta['imdb_id'], 'title': vidtitle, 'name': vidname, 'season': season_num}, meta, properties=properties, contextmenu_items=contextMenuItems, context_replace=True, img=meta['cover_url'], fanart=meta['backdrop_url'], total_items=totalitems)


def add_video_item(video_type, section, link, vidtitle, vidname, metaget=None, year='', imdb='', season_num=0, episode_num=0, totalitems=0, favourite=False):
        
    meta = get_metadata(video_type, vidtitle,  metaget=metaget, vidname=vidname, year=year, imdb=imdb, season_num=season_num, episode_num=episode_num)
    if video_type == VideoType_Movies:
        contextMenuItems = add_contextmenu(meta_setting, video_type, link, vidtitle, meta['title'], favourite, watched=meta['overlay'], imdb=meta['imdb_id'], year=meta['year'])
    else:
        contextMenuItems = add_contextmenu(meta_setting, video_type, link, vidtitle, meta['title'], favourite, watched=meta['overlay'], imdb=meta['imdb_id'], season_num=season_num, episode_num=episode_num)

    if video_type == VideoType_Movies:
        addon.add_video_item({'url': link, 'video_type': video_type, 'section': section, 'title': vidtitle, 'name': vidname}, meta, contextmenu_items=contextMenuItems, context_replace=True, img=meta['cover_url'], fanart=meta['backdrop_url'], total_items=totalitems)
    elif video_type == VideoType_Episode:
        addon.add_video_item({'url': link, 'video_type': video_type, 'section': section, 'title': vidtitle, 'name': vidname}, meta, contextmenu_items=contextMenuItems, context_replace=True, img=meta['cover_url'], fanart=meta['backdrop_url'], total_items=totalitems)


# Create A-Z Menu
def AZ_Menu(type, url):
     
    addon.add_directory({'mode': type, 
                         'url': url + 'numeric.html', 'letter': '#'},{'title': '#'},
                         img=icon_path("0.png"))
    for l in string.uppercase:
        addon.add_directory({'mode': type, 
                             'url': url + str(l.lower()) + '.html', 'letter': l}, {'title': l},
                             img=icon_path(l + ".png"))


# Get List of Movies from given URL
def GetMovieList(url):

    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None

    html = get_html(url)
    match = re.compile('<td width="97%" class="mnlcategorylist"><a href="(.+?)"><b>(.+?)[ (]*([0-9]{0,4})[)]*</b></a>(.+?)<').findall(html)

    for link, vidname, year, numlinks in match:
       if re.search("../",link) is not None:
          link = link.strip('\n').replace("../","")
          newUrl = MovieUrl + link
       else:
          newUrl = url + "/" + link
       add_video_item(VideoType_Movies, VideoType_Movies, newUrl, vidname, vidname, metaget=metaget, totalitems=len(match))
    setView('movies', 'movie-view')

if play:

    try:
        import urlresolver
    except:
        addon.log_error("Failed to import script.module.urlresolver")
        xbmcgui.Dialog().ok("PFTV Import Failure", "Failed to import URLResolver", "A component needed by PFTV is missing on your system", "Please visit www.xbmchub.com for support")
    
    sources = []
    html = get_html(url)
           
    if section == 'movies':
        
        #Check for trailers
        match = re.compile('<a target="_blank" style="font-size:9pt" class="mnlcategorylist" href=".+?id=(.+?)">(.+?)</a>&nbsp;&nbsp;&nbsp;').findall(html)
        for linkid, vidname in match:      
            media = urlresolver.HostedMediaFile(host='youtube', media_id=linkid, title=vidname)
            sources.append(media)        
     
    elif section == 'latestmovies':
        #Search within HTML to only get portion of links specific to movie name
        # TO DO - currently does not return enough of the header for the first link
        r = re.search('<div>%s</div>(.+?)(<div>(?!%s)|<p align="center">)' % (re.escape(title), re.escape(title)), html, re.DOTALL)
        if r:
            html = r.group(0)
        else:
            html = ''
    
    elif section in ('tvshows', 'episode'):
        #Search within HTML to only get portion of links specific to episode requested
        r = re.search('<td class="episode"><b>%s</b></td>(.+?)(<tr bgcolor="#E3E3E3">|<p align="center">)' % re.escape(name), html, re.DOTALL) 
        #r = re.search('<td class="episode"><a name=".+?"></a><b>%s</b>(.+?)(<a name=|<p align="center">)' % re.escape(name), html, re.DOTALL) 
        if r:
            html = r.group(1)
        else:
            html = ''   
    
    #Now Add video source links
    match = re.compile('<a class="mnllinklist" target="_blank" href="(.+?)">.+?Loading Time: <span class=".+?">(.+?)</span>[\r\n ]*<br />[\r\n ]*Host: (.+?)[\r\n ]*<br/>.+?class="report">.+?([0-9]*[0-9]%) Said Work', re.DOTALL).findall(html)
    #match = re.compile('<a onclick=\'.+?\' href=".+?id%3D(.+?)&.+?" target=".+?<div>.+?(|part [0-9]* of [0-9]*)</div>.+?<span class=\'.*?\'>(.*?)</span>.+?Host: (.+?)<br/>.+?class="report">.+?([0-9]*[0-9]%) Said Work', re.DOTALL).findall(html)
    links = []
    for link, load, host, working in match:
    #for linkid, vidname, load, host, working in match:
        # if vidname:
           # vidname = vidname.title()
        # else:
           # vidname = 'Full'
        vidname = 'Full'           
        #media = urlresolver.HostedMediaFile(host=host, media_id=linkid, title=vidname + ' - ' + host + ' - ' + load + ' - ' + working)
        #sources.append(media)
        
        sources.append(vidname + ' - ' + host + ' - ' + load + ' - ' + working)
        links.append(link)

    dialog = xbmcgui.Dialog()
    index = dialog.select('Choose your stream:', sources)

    source = None
    if index > -1:
        html = get_html(MainUrl + links[index])
        link = re.search('src="(.+?)".+?></iframe>', html, re.IGNORECASE)
        
        if link:
            source=link.group(1)
    
    #source = urlresolver.choose_source(sources)

    if source:
        stream_url = urlresolver.resolve(source)
    else:
        stream_url = False

        
    #Play the stream
    if stream_url:
        addon.resolve_url(stream_url)


if mode == 'main': 
    addon.add_directory({'mode': 'movies', 'section': 'movies'}, {'title':  'Movies'}, img=icon_path('Movies.png'))
    addon.add_directory({'mode': 'tv', 'section': 'tv'}, {'title': 'TV Shows'}, img=icon_path('TV_Shows.png'))
    addon.add_directory({'mode': 'search', 'section': SearchAll}, {'title': 'Search All'}, img=icon_path('Search.png'))
    addon.add_directory({'mode': 'resolver_settings'}, {'title':  'Resolver Settings'}, is_folder=False, img=icon_path('Settings.png'))
    setView(None, 'default-view')


elif mode == 'movies':
    addon.add_directory({'mode': 'favourites', 'video_type': VideoType_Movies}, {'title': 'Favourites'}, img=icon_path("Favourites.png"))
    addon.add_directory({'mode': 'movieslatest', 'section': 'movieslatest'}, {'title': 'Latest Added Links'}, img=icon_path("Latest_Added.png"))
    addon.add_directory({'mode': 'moviesaz', 'section': 'moviesaz'}, {'title': 'A-Z'}, img=icon_path("AZ.png"))
    addon.add_directory({'mode': 'moviesgenre', 'section': 'moviesgenre'}, {'title': 'Genre'}, img=icon_path('Genre.png'))
    addon.add_directory({'mode': 'moviesyear', 'section': 'moviesyear'}, {'title': 'Year'}, img=icon_path('Year.png'))
    addon.add_directory({'mode': 'search', 'section': SearchMovies}, {'title': 'Search'}, img=icon_path('Search.png'))
    setView(None, 'default-view')


elif mode == 'moviesaz':
    AZ_Menu('movieslist', MovieUrl + 'browse/')
    setView(None, 'default-view')


elif mode == 'moviesgenre':
    url = MovieUrl
    html = get_html(url)
    match = re.compile('<a class ="genre" href="/(.+?)"><b>(.+?)</b></a><b>').findall(html)

    # Add each link found as a directory item
    for link, genre in match:
        addon.add_directory({'mode': 'movieslist', 'url': MainUrl + link, 'section': 'movies'}, {'title': genre})
    setView(None, 'default-view')


elif mode == 'movieslatest':

    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None
    latestlist = []
    url = MovieUrl
    html = get_html(url)
        
    match = re.compile('''<a onclick='visited.+?' href=".+?" target=.+?<div>(.+?)</div>''',re.DOTALL).findall(html)
    for vidname in match:
        latestlist.append(vidname)

    #convert list to a set which removes duplicates, then back to a list
    latestlist = list(set(latestlist))

    for movie in latestlist:
        add_video_item(VideoType_Movies, 'latestmovies', url, movie, movie, metaget=metaget, totalitems=len(match))
    setView('movies', 'movie-view')


elif mode == 'moviesyear':
    url = MovieUrl
    html = get_html(url)
    match = re.compile('''<td width="97%" nowrap="true" class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a></td>''').findall(html)

    # Add each link found as a directory item
    for link, year in match:
       addon.add_directory({'mode': 'movieslist', 'url': url + urllib.quote(link), 'section': 'movies'}, {'title': year})
    setView(None, 'default-view')


elif mode == 'movieslist':
   GetMovieList(url)


elif mode == 'tv':
    addon.add_directory({'mode': 'favourites', 'video_type': VideoType_TV}, {'title': 'Favourites'}, img=icon_path("Favourites.png"))
    addon.add_directory({'mode': 'tvseries_upc', 'section': 'tvseries_upc'}, {'title': 'Upcoming Episodes'}, img=icon_path('Upcoming.png'))
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv24hours', 'url': TVUrl + 'index_last.html'}, {'title': 'Last 24 Hours'}, img=icon_path('Last_24_Hours.png'))
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv3days', 'url': TVUrl + 'index_last_3_days.html'}, {'title': 'Last 3 Days'}, img=icon_path('Last_3_Days.png'))
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv7days', 'url': TVUrl + 'index_last_7_days.html'}, {'title': 'Last 7 Days'}, img=icon_path('Last_7_Days.png'))
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tvmonth', 'url': TVUrl + 'index_last_30_days.html'}, {'title': 'This Month'}, img=icon_path('This_Month.png'))
    addon.add_directory({'mode': 'tvlastadded', 'section': 'tv90days', 'url': TVUrl + 'index_last_365_days.html'}, {'title': 'Last 90 Days'}, img=icon_path('Last_90_Days.png'))
    addon.add_directory({'mode': 'tvpopular', 'section': 'tvpopular'}, {'title': 'Popular'}, img=icon_path('Popular.png'))
    addon.add_directory({'mode': 'tvseries_all', 'section': 'tvseries_all'}, {'title': 'All'}, img=icon_path('All_Shows.png'))
    addon.add_directory({'mode': 'tvaz', 'section': 'tvaz'}, {'title': 'A-Z'}, img=icon_path("AZ.png"))
    addon.add_directory({'mode': 'search', 'section': SearchTV}, {'title': 'Search'}, img=icon_path('Search.png'))
    setView(None, 'default-view')


elif mode == 'tvaz':
    AZ_Menu('tvseries-az',TVUrl)
    setView(None, 'default-view')


elif mode == 'tvseries-az':
    url = TVUrl
    letter = addon.queries['letter']
    
    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None
        
    html = get_html(url)
    r = re.search('<a name="%s">(.+?)(<a name=|</table>)' % letter, html, re.DOTALL)
    
    if r:
        match = re.compile('class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a> (<sub>New Episode!</sub>|)</td>').findall(r.group(1))
        for link, vidtitle, newep in match:
            vidname = vidtitle
            if newep:
                vidname = vidtitle + ' [COLOR red]New Episode![/COLOR]'
            add_video_directory('tvseasons', VideoType_TV, TVUrl + link, vidtitle, vidname, metaget=metaget, totalitems=len(match))
    setView('tvshows', 'tvshow-view')


elif mode == 'tvseries_all':
    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None

    url = TVUrl
    html = get_html(url)
    
    match = re.compile('class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a> (<sub>New Episode!</sub>|)</td>').findall(html)
    for link, vidtitle, newep in match:
        vidname = vidtitle
        if newep:
            vidname = vidtitle + ' [COLOR red]New Episode![/COLOR]'
        add_video_directory('tvseasons', VideoType_TV, TVUrl + link, vidtitle, vidname, metaget=metaget, totalitems=len(match))
    setView('tvshows', 'tvshow-view')


elif mode == 'tvseries_upc':
    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None

    url = TVUrl
    html = get_html(url)

    html = re.search('<link rel="stylesheet" href="/css/schedule1.css" type="text/css">(.+?)</table>', html, re.DOTALL)
    if html:
        today = False
        sched_match = re.compile('<td width="14%" class="(schedule[ today]*)">[\r\n\t ]*<span class="sheader">(.+?)</span>[\r\n\t ]*<span class="sdate">(.+?)</span>(.+?)</td>', re.DOTALL).findall(html.group(1))
        for schedule, day, date, episodes in sched_match:
            
            if schedule == 'schedule today':
                today = True
                addon.add_directory({'mode': 'none'}, {'title': '[COLOR red] %s %s[/COLOR]' % (day.strip(), date.strip())}, is_folder=False, img='')
            elif not schedule == 'schedule today' and today:
                addon.add_directory({'mode': 'none'}, {'title': '[COLOR blue] %s %s[/COLOR]' % (day.strip(), date.strip())}, is_folder=False, img='')
            
            if today:
                #ep_match = re.compile('<a href=\'/(.+?)\' title="(.+? S([0-9]+)E([0-9]+) .+?)" class=\'epp\'>(.+?)</a>').findall(episodes)
                ep_match = re.compile('<a class="epp" href="(.+?)">(.+?)</a>').findall(episodes)
                #for link, vidname, season_num, episode_num, vidtitle in ep_match:
                for link, vidtitle in ep_match:
    
                    #Since we are getting season level items, try to grab the imdb_id of the TV Show first to make meta get easier
                    if meta_setting:
                        meta = get_metadata(VideoType_TV, vidtitle, metaget=metaget)
                        imdb = meta['imdb_id']
                    else:
                        imdb = ''
                    
                    #They give a link to the show, but not the correct season, let's fix that
                    #new_url = MainUrl + link + 'season_' + str(int(season_num)) + '.html'
                    add_video_directory('tvseasons', VideoType_Season, MainUrl + link, vidtitle, vidtitle, metaget=metaget, imdb=imdb, totalitems=(len(sched_match) * len(ep_match)))
    setView('seasons', 'season-view')


elif mode == 'tvlastadded':

    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None
        
    html = get_html(url)
    #full_match = re.compile('class="mnlcategorylist"><a href="(.+?)#.+?"><b>((.+?) - Season ([0-9]+) Episode ([0-9]+)) <').findall(html)
    full_match = re.compile('class="mnlcategorylist">[\r\n ]*<a href="(.+?)[#]*.*?">[\r\n ]*<b>((.+?) - Season ([0-9]+) Episode ([0-9]+))<', re.DOTALL).findall(html)
    match = re.compile('<a name="*(.+?)"></a>(.+?)(?:<td colspan="2">|</table>)', re.DOTALL).findall(html)
    for added_date, inside_html in match:
        addon.add_directory({'mode': 'none'}, {'title': '[COLOR blue]' + added_date + '[/COLOR]'}, is_folder=False, img='')
        inside_match = re.compile('class="mnlcategorylist">[\r\n ]*<a href="(.+?)">[\r\n ]*<b>((.+?) [\(]*([0-9]{0,4})[\) ]*- Season ([0-9]+) Episode ([0-9]+))<').findall(inside_html)
        for link, vidname, vidtitle, year, season_num, episode_num in inside_match:
            #Since we are getting season level items, try to grab the imdb_id of the TV Show first to make meta get easier
            if meta_setting:
                meta = get_metadata(VideoType_TV, vidtitle, metaget=metaget, year=year)
                imdb = meta['imdb_id']
            else:
                imdb = ''

            #They give a link to the show, but not always to the correct season, let's fix that
            import urlparse
            split_url = urlparse.urlsplit(link)        
            if not split_url.fragment:
                link = link + '/season_' + str(int(season_num)) + '.html'
            
            if link.startswith(TVPath):
                newLink = MainUrl + link
            else:
                newLink = TVUrl + link
            add_video_directory('tvepisodes', VideoType_Season, newLink, vidtitle, vidname, metaget=metaget, imdb=imdb, season_num=season_num, totalitems=len(full_match))
    setView('seasons', 'season-view')    


elif mode == 'tvpopular':

    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None
        
    url = MainUrl
    html = get_html(url)
    match = re.compile('<td class="tleft".*?><a href="(.+?)/">(.+?)</a></td>').findall(html)
    for link, vidname in match:
        is_tv = re.search('/internet/', link)
        if vidname != "...more" and is_tv:
            add_video_directory('tvseasons', VideoType_TV, link, vidname, vidname, metaget=metaget, totalitems=len(match))
    setView('tvshows', 'tvshow-view')    


elif mode == 'tvseasons':
    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None
        
    if url.startswith('http') == False:
        url = MainUrl + url
    html = get_html(url)
    match = re.compile('class="mnlcategorylist">.*?<a href="(.+?)"><b>(.+?)</b></a>(.+?)<', re.DOTALL).findall(html)
    seasons = re.compile('class="mnlcategorylist">.*?<a href=".+?"><b>Season ([0-9]+)</b></a>.+?<', re.DOTALL).findall(html)
    #seasons = list(xrange(len(match)))
    
    #If we have more matches than seasons found then we might have an extra 'special' season, add it as Season '0'
    if len(match) > len(seasons):
        seasons.insert(0,'0')

    season_meta = {}    
    if meta_setting:
        season_meta = get_metadata(video_type, title, metaget=metaget, imdb=imdb_id, season_list=seasons)
    else:
        meta = {}
        meta['TVShowTitle'] = title
        meta['cover_url'] = ''
        meta['imdb_id'] = ''
        meta['backdrop_url'] = ''
        meta['overlay'] = 0
        
    num = 0
    for link, season_num, episodes in match:
        is_season = re.search('Season ([0-9]+)', season_num)
        if season_meta and is_season:
            meta = season_meta[num]
        else:
            num = num - 1
            meta = {}
            meta['TVShowTitle'] = title
            meta['cover_url'] = ''
            meta['imdb_id'] = ''
            meta['backdrop_url'] = ''
            meta['overlay'] = 0
        meta['title'] = season_num + episodes
        link = MainUrl + link
        contextMenuItems = add_contextmenu(meta_setting, video_type, link, title, meta['title'], favourite=False, watched=meta['overlay'], imdb=meta['imdb_id'], season_num=seasons[num])
        addon.add_directory({'mode': 'tvepisodes', 'url': link, 'video_type': VideoType_Season, 'imdb_id': meta['imdb_id'], 'title': title, 'name': meta['title'], 'season': seasons[num]}, meta, contextmenu_items=contextMenuItems, context_replace=True, img=meta['cover_url'], fanart=meta['backdrop_url'], total_items=len(match))
        num = num + 1
    setView('seasons', 'season-view')


elif mode == 'tvepisodes':
    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None
        
    html = get_html(url)

    match = re.compile('<td class="episode">(.*?)<b>(.+?)</b></td>[\r\n ]*<td align="right" class="mnllinklist">[\r\n ]*<div class="right">.+Air Date: (.+?)</div>').findall(html)
    #match = re.compile('<td class="episode">.*?<a name=".+?"></a>(.*?)<b>(.+?)</b></td>[\r\n\t]*(<td align="right".+?Air Date: (.*?)</div>)*', re.DOTALL).findall(html)
    for next_episode, vidname, next_air in match:
        print vidname
        episode_num = re.search('([0-9]{0,2})\.', vidname)
        if episode_num:
            episode_num = episode_num.group(1)
        else:
            episode_num = 0
        if not next_episode:
            add_video_item(VideoType_Episode, VideoType_Episode, url, title, vidname, metaget=metaget, imdb=imdb_id, season_num=season, episode_num=episode_num, totalitems=len(match))
        else:
            meta = get_metadata(VideoType_Episode, title, metaget=metaget, vidname=vidname, imdb=imdb_id, season_num=season, episode_num=episode_num)
            if next_air: 
                meta['title'] = '[COLOR blue]Next Episode: %s - %s[/COLOR]' % (next_air, vidname)
            addon.add_directory({'mode': 'none'}, meta, is_folder=False, img=meta['cover_url'], fanart=meta['backdrop_url'])            
    setView('episodes', 'episode-view')


elif mode == 'search':

    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None

    index = 0
    search_text = ""
    search_list = []
    new_search = False

    #Check first if a 'name' has been passed in - signals an adhoc search request
    if name:
        new_search = True
        search_text = name
    else:
        search_hist = cache.get('search_' + section)
       
        #Convert returned string back into a list
        if search_hist:
            try:
                search_list = eval(search_hist)
            except:
                search_list.insert(0, search_hist)

    #If we have historical search items, prompt the user with list
    if search_list:
        dialog = xbmcgui.Dialog()
        
        #Add a place holder at list index 0 for allowing user to do new searches
        tmp_search_list = list(search_list)
        tmp_search_list.insert(0, 'New Search')
        index = dialog.select('Select Search', tmp_search_list)

        #If index is 0 user selected New Search, if greater than user selected existing item
        if index > 0:
            search_text = tmp_search_list[index]
        elif index == 0:
            new_search = True

    #If a new search is required, bring up the keyboard
    if (not search_text and not index == -1) or new_search:
        kb = xbmc.Keyboard(search_text, 'Search Project Free TV - %s' % section.capitalize(), False)
        kb.doModal()
        if (kb.isConfirmed()):                   
            search_text = kb.getText()

    #If we have some text to search by, lets do it
    if search_text:

        #Add to our search history only if it doesn't already exist
        if search_text not in search_list:
            search_list.insert(0, search_text)
            
            #Lets keep just 10 search history items at a time
            if len(search_list) > 10:
                del search_list[10]
            
            #Write the list back to cache
            cache.set('search_' + section, str(search_list))

        search_quoted = urllib.quote(search_text)
        url = SearchUrl % (search_quoted, section)
        html = get_html(url)
        
        #match = re.compile('<td width="97%" class="mnlcategorylist">[\r\n\t]*<a href="(.+?)">[\r\n\t]*<b>(.+?)[ (]*([0-9]{0,4})[)]*</b>').findall(html)
        match = re.compile('<td width="99%" class="mnlcategorylist"><a href="(.+?)"><b>(.+?)</b></a>').findall(html)
        if match:
            #for link, vidname, year in match:
            for link, vidname in match:
                link = MainUrl + link
                if re.search('/movies/', link):
                    #add_video_item(VideoType_Movies, VideoType_Movies, link, vidname, vidname, metaget=metaget, year=year, totalitems=len(match))
                    add_video_item(VideoType_Movies, VideoType_Movies, link, vidname, vidname, metaget=metaget, totalitems=len(match))
                else:
                    #add_video_directory('tvseasons', VideoType_TV, link, vidname, vidname, metaget=metaget, year=year, totalitems=len(match))
                    add_video_directory('tvseasons', VideoType_TV, link, vidname, vidname, metaget=metaget, totalitems=len(match))
        else:
            Notify('small', 'No Results', 'No search results found','')
    setView(None, 'default-view')


elif mode == 'favourites':
    if meta_setting:
        metaget=metahandlers.MetaData()
    else:
        metaget=None

    #Add Season/Episode sub folders
    if video_type == VideoType_TV:
        addon.add_directory({'mode': 'favourites', 'video_type': VideoType_Season}, {'title': '[COLOR blue]Seasons[/COLOR]'})
        addon.add_directory({'mode': 'favourites', 'video_type': VideoType_Episode}, {'title': '[COLOR blue]Episodes[/COLOR]'})

    #Grab saved favourites from DB and populate list
    saved_favs = cache.get('favourites_' + video_type)
    if saved_favs:
        favs = sorted(eval(saved_favs), key=lambda fav: fav[1])
        for fav in favs:
            
            import urlparse
            split_url = urlparse.urlsplit(fav[5])                
            new_url = MainUrl + split_url.path
            
            if video_type in (VideoType_Movies, VideoType_Episode):
                add_video_item(video_type, video_type, new_url, fav[0], fav[1], metaget=metaget, imdb=fav[2], season_num=fav[3], episode_num=fav[4], totalitems=len(favs), favourite=True)
            elif video_type == VideoType_TV:
                add_video_directory('tvseasons', video_type, new_url, fav[0], fav[1], metaget=metaget, imdb=fav[2], season_num=fav[3], totalitems=len(favs), favourite=True)
            elif video_type == VideoType_Season:
                add_video_directory('tvepisodes', video_type, new_url, fav[0], fav[1], metaget=metaget, imdb=fav[2], season_num=fav[3], totalitems=len(favs), favourite=True)
    setView(video_type +'s', video_type + '-view')


elif mode == 'add_fav':
    add_favourite()


elif mode == 'del_fav':
    remove_favourite()


elif mode == 'refresh_meta':
    if video_type == VideoType_Movies:
        refresh_movie(title)

    elif video_type == VideoType_TV:
        refresh_tv(title, imdb_id) 
    elif video_type == VideoType_Season:
        season_refresh(title, imdb_id, season)
    elif video_type == VideoType_Episode:
        episode_refresh(title, imdb_id, season, episode)


elif mode == 'watch_mark':
    metaget=metahandlers.MetaData()
    metaget.change_watched(video_type, title, imdb_id, season=season, episode=episode)
    xbmc.executebuiltin("Container.Refresh")


elif mode == 'resolver_settings':
    import urlresolver
    urlresolver.display_settings()


elif mode=='meta_settings':
        print "Metahandler Settings"
        import metahandler
        metahandler.display_settings()


elif mode=='delete_favs':
        
        dialog = xbmcgui.Dialog()
        ret = dialog.yesno('Delete Favourites', 'Do you wish to delete %s PFTV Favourites?' % video_type.upper(), '','This cannot be undone!')        

        if ret == True:
            addon.log("Deleting favourites: %s" % video_type)
            if video_type == 'all':
                cache.delete('favourites_%s' % VideoType_Movies)
                cache.delete('favourites_%s' % VideoType_TV)
                cache.delete('favourites_%s' % VideoType_Season)
                cache.delete('favourites_%s' % VideoType_Episode)
            else:
                cache.delete('favourites_%s' % video_type)
            Notify('small', 'PFTV Favourites', 'PFTV %s Favourites Deleted' % video_type.title())


elif mode=='delete_search_history':
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('Delete Search History', 'Do you wish to delete PFTV Search History', '','This cannot be undone!')

    if ret == True:
      addon.log("Deleting search history")
      try:
          cache.delete('search_all')
          cache.delete('search_movies')
          cache.delete('search_shows')
          Notify('small', 'PFTV History', 'PFTV Search History Deleted')
      except Exception, e:
          addon.log("Failed to delete search history: %s" % e)
          Notify('big', 'PFTV History', 'Error deleting PFTV search history')


if not play:
    addon.end_of_directory()