import xbmc, xbmcgui, xbmcaddon, xbmcplugin
import urllib, urllib2
import re, string, sys, os
import commonresolvers
import urlresolver
from t0mm0.common.addon import Addon
from t0mm0.common.net import Net
from htmlentitydefs import name2codepoint as n2cp
import HTMLParser

try:
        from sqlite3 import dbapi2 as sqlite
        print "Loading sqlite3 as DB engine"
except:
        from pysqlite2 import dbapi2 as sqlite
        print "Loading pysqlite2 as DB engine"

addon_id = 'plugin.video.pencarimovie.my'
plugin = xbmcaddon.Addon(id=addon_id)
#DB = os.path.join(xbmc.translatePath("special://database"), 'dfv.db')
BASE_URL = 'http://pencarimovie.pe.hu'
net = Net()
addon = Addon('plugin.video.pencarimovie.my', sys.argv)

###### PATHS ###########
AddonPath = addon.get_path()
IconPath = AddonPath + "/icons/"
FanartPath = AddonPath + "/icons/"

##### Queries ##########
mode = addon.queries['mode']
url = addon.queries.get('url', None)
content = addon.queries.get('content', None)
query = addon.queries.get('query', None)
startPage = addon.queries.get('startPage', None)
numOfPages = addon.queries.get('numOfPages', None)
listitem = addon.queries.get('listitem', None)
urlList = addon.queries.get('urlList', None)
section = addon.queries.get('section', None)

################################################################################# Titles #################################################################################

def GetTitles(section, url, startPage= '1', numOfPages= '1'):
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        searchurl = url.split("?")
        searchurl = searchurl[0]
        match = re.search('pencarimovie', url)
        if match:
           searchurl =  BASE_URL
        if int(startPage)> 1:
                pageUrl = url + '/page/' + startPage
        print pageUrl
        html = net.http_GET(pageUrl).content
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + '/page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content
                match = re.compile('moviefilm.+?href="(.+?)".+?src="(.+?)" alt="(.+?)".+?', re.DOTALL).findall(html)
                addon.add_directory({'mode': 'GetSearchQuery', 'url': searchurl},  {'title':  '[COLOR green]Search[/COLOR]'}, img=IconPath + 'searchmy.png', fanart=FanartPath + 'fanart.png')
                for movieUrl, img, name in match:
                        addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png')
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

################################################################################# Episode #################################################################################

def GetEpisode(section, url, startPage= '1', numOfPages= '1'):
        print 'Proses penyenaraian tajuk cerita %s' % url
        pageUrl = url
        if int(startPage)> 1:
                pageUrl = url + '/page/' + startPage
        print pageUrl
        searchurl = url.split("?")
        html = net.http_GET(pageUrl).content
        start = int(startPage)
        end = start + int(numOfPages)
        for page in range( start, end):
                if ( page != start):
                        pageUrl = url + '/page/' + str(page) + '/'
                        html = net.http_GET(pageUrl).content
                match = re.compile('moviefilm.+?href="(.+?)".+?src="(.+?)" alt="(.+?)".+?', re.DOTALL).findall(html)
                addon.add_directory({'mode': 'GetSearchQuery', 'url': searchurl[0]},  {'title':  '[COLOR green]Search[/COLOR]'}, img=IconPath + 'searchmy.png', fanart=FanartPath + 'fanart.png')
                for movieUrl, img, name in match:
                        addon.add_directory({'mode': 'GetEpisodelinks', 'section': section, 'url': movieUrl}, {'title':  name.strip()}, img= img, fanart=FanartPath + 'fanart.png')
                addon.add_directory({'mode': 'GetTitles', 'url': url, 'startPage': str(end), 'numOfPages': numOfPages}, {'title': '[COLOR blue][B][I]Next page...[/B][/I][/COLOR]'}, img=IconPath + 'next.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        
############################################################################### Get Episodelinks #############################################################################

def GetEpisodelinks(section, url):
        print 'GETLINKS FROM URL: '+url
        html = net.http_GET(url).content
        listitem = GetMediaInfo(html)
        content = html
        match = re.compile('<p><a title="(.+?)" href="(.+?)" target=".+?">.+?</a></p>').findall(content)
        listitem = GetMediaInfo(content)
        for name, url in match:
                r = re.search('', content)
                if r: addon.add_directory({'mode': 'GetLinks', 'section': section, 'url': BASE_URL +url}, {'title':  name.strip()}, fanart=FanartPath + 'fanart.png')
                else:
                       host = GetDomain(BASE_URL +url)
                       if urlresolver.HostedMediaFile(url= url):addon.add_directory({'mode': 'PlayVideo', 'url': BASE_URL +url, 'listitem': listitem}, {'title':  host }, img=IconPath + 'playmy.png', fanart=FanartPath + 'fanart.png')
        
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################### Get links ###################################################################################


def GetLinks(section, url):
        print 'GETLINKS FROM URL: '+url
        html = net.http_GET(url).content
        listitem = GetMediaInfo(html)
        content = html
        match = re.compile('<p align="center"><iframe src="(.+?)" .+?').findall(content)
        listitem = GetMediaInfo(content)
        for url in match:
                host = GetDomain(url)
                if urlresolver.HostedMediaFile(url= url):addon.add_directory({'mode': 'PlayVideo', 'url': url, 'listitem': listitem}, {'title':  host }, img=IconPath + 'playmy.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

############################################################################# Play Video #####################################################################################

def PlayVideo(url, listitem):
    try:
        print 'in PlayVideo %s' % url
        stream_url = urlresolver.HostedMediaFile(url).resolve()
        #stream_url = commonresolvers.get(url).result
        xbmc.Player().play(stream_url)
        addon.add_directory({'mode': 'help'}, {'title':  '[COLOR slategray][B]^^^ Press back ^^^[/B] [/COLOR]'},'','')
    except:
        xbmc.executebuiltin("XBMC.Notification([COLOR red][B]Sorry Link may have been removed ![/B][/COLOR],[COLOR lime][B]Please try a different link/host !![/B][/COLOR],7000,"")")

def myinfo():
    dialog = xbmcgui.Dialog()
    dialog.ok(" PENCARIMOVIE", "Admin: Faizal Ahmad ", "Email: faiztutorial91@gmail.com", "Blog: http://faiz-tutorial.blogspot.com")
    MainMenu()

def GetDomain(url):
        tmp = re.compile('//(.+?)/').findall(url)
        domain = 'Unknown'
        if len(tmp) > 0 :
            domain = tmp[0].replace('www.', '')
        return domain

def GetMediaInfo(html):
        listitem = xbmcgui.ListItem()
        match = re.search('og:title" content="(.+?) \((.+?)\)', html)
        if match:
                print match.group(1) + ' : '  + match.group(2)
                listitem.setInfo('video', {'Title': match.group(1), 'Year': int(match.group(2)) } )
        return listitem

###################################################################### menus ####################################################################################################

def MainMenu():    #homescreen

        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/category/mymovie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Movie'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/category/mytelemovie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Telemovie'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/category/dramalist/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Drama'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')	
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/category/tvshowlist/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'TV Show'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/category/layarklasik/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Layar Klasik'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/category/layarretro/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Filem Retro'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'GetEpisode', 'section': 'ALL', 'url': BASE_URL + '/category/animasilist/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Animasi'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')								 					 								 						 
        addon.add_directory({'mode': 'GetTitles', 'section': 'ALL', 'url': BASE_URL + '/category/Indomovie/',
                             'startPage': '1', 'numOfPages': '1'}, {'title':  'Indo Movie'}, img=IconPath + 'folder.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'ResolverSettings'}, {'title':  '[COLOR red]Resolver Settings[/COLOR]'}, img=IconPath + 'set.png', fanart=FanartPath + 'fanart.png')
        addon.add_directory({'mode': 'myinfo'}, {'title':  '[COLOR yellow]INFO[/COLOR]'}, img=IconPath + 'info.png', fanart=FanartPath + 'fanart.png')
        xbmcplugin.endOfDirectory(int(sys.argv[1]))



#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------#

def GetSearchQuery(url):
	url = url + '/?s='
    #last_search = addon.load_data('search')
	#if not last_search: last_search = ''
	keyboard = xbmc.Keyboard()
        keyboard.setHeading('[COLOR green]Search[/COLOR]')
	#keyboard.setDefault(last_search)
	keyboard.doModal()
	if (keyboard.isConfirmed()):
                query = keyboard.getText()
                addon.save_data('search',query)
                url = url + query
                GetTitles(section, url, startPage= '1', numOfPages= '1')
                #Search(query,url)
	else:
                return  
def Search(query,url):
        url = url + query
        url = url.replace(' ', '+')
        print url
        html = net.http_GET(url).content
        match = re.compile('moviefilm.+?href="(.+?)".+?src="(.+?)" alt="(.+?)".+?').findall(html)
        for url, title in match:
                title = title.replace('<b>...</b>', '').replace('<em>', '').replace('</em>', '')
                addon.add_directory({'mode': 'GetLinks', 'url': url}, {'title':  title})
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


#################################################################################################################################################################################

if mode == 'main':
        MainMenu()
elif mode == 'myinfo':
        myinfo()
elif mode == 'GetTitles':
        GetTitles(section, url, startPage, numOfPages)
elif mode == 'GetEpisode':
        GetEpisode(section, url, startPage, numOfPages)
elif mode == 'GetEpisodelinks':
        GetEpisodelinks(section, url)        
elif mode == 'GetLinks':
        GetLinks(section, url)
elif mode == 'GetSearchQuery':
        GetSearchQuery(url)
elif mode == 'Search':
        Search(query,url)
elif mode == 'PlayVideo':
        PlayVideo(url, listitem)        
elif mode == 'ResolverSettings':
        urlresolver.display_settings()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
