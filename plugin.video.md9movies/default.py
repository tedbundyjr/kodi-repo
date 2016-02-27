import urllib,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,os
import requests
from addon.common.addon import Addon
from addon.common.net import Net
from metahandler import metahandlers

#9Movies Add-on Created By Mucky Duck (12/2015)

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
addon_id='plugin.video.md9movies'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = Addon(addon_id, sys.argv)
art = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id + '/resources/art/'))
icon = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id, 'icon.png'))
fanart = xbmc.translatePath(os.path.join('special://home/addons/' + addon_id , 'fanart.jpg'))
metaset = selfAddon.getSetting('enable_meta')
show_tv = selfAddon.getSetting('enable_shows')
metaget = metahandlers.MetaData()
baseurl = 'http://9movies.to/'
net = Net()



def CAT():
        addDir('[B][COLOR white]Most Watched[/COLOR][/B]',baseurl+'/filter?sort=views&type%5B%5D=movie',1,icon,fanart,'')
        addDir('[B][COLOR white]Country[/COLOR][/B]',baseurl,7,icon,fanart,'')
        addDir('[B][COLOR white]Search[/COLOR][/B]','url',4,icon,fanart,'')
        addDir('[B][COLOR white]Latest[/COLOR][/B]',baseurl+'/filter?sort=post_date&type%5B%5D=movie',1,icon,fanart,'')
        addDir('[B][COLOR white]Genre[/COLOR][/B]',baseurl,5,icon,fanart,'')
        addDir('[B][COLOR white]Year[/COLOR][/B]',baseurl,8,icon,fanart,'')
        addDir('[B][COLOR white]A/Z[/COLOR][/B]',baseurl+'/filter?sort=title&type%5B%5D=movie',1,icon,fanart,'')
        if show_tv == 'true':
                addDir('[B][COLOR white]TV[/COLOR][/B]','url',9,icon,fanart,'')




def TV():
        addDir('[B][COLOR white]Most Watched[/COLOR][/B]',baseurl+'/filter?sort=views&type%5B%5D=series',2,icon,fanart,'')
        addDir('[B][COLOR white]Released[/COLOR][/B]',baseurl+'/filter?sort=release&type%5B%5D=series',2,icon,fanart,'')
        addDir('[B][COLOR white]Search[/COLOR][/B]','url',10,icon,fanart,'')
        addDir('[B][COLOR white]Latest[/COLOR][/B]',baseurl+'/filter?sort=post_date&type%5B%5D=series',2,icon,fanart,'')
        #addDir('[B][COLOR white]Genre[/COLOR][/B]',baseurl,,icon,fanart,'')
        #addDir('[B][COLOR white]Year[/COLOR][/B]',baseurl,,icon,fanart,'')
        addDir('[B][COLOR white]A/Z[/COLOR][/B]',baseurl+'/filter?sort=title&type%5B%5D=series',2,icon,fanart,'')
        


def INDEX(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore').decode('ascii')
        all_videos = regex_get_all(link, '<a class="thumb"', '</li>')
        items = len(all_videos)
        for a in all_videos:
                name = regex_from_to(a, 'title="', '"').replace("&amp;","&").replace('&#39;',"'").replace('&quot;','"').replace('&#039;',"'")
                url = regex_from_to(a, 'href="', '"').replace("&amp;","&")
                thumb = regex_from_to(a, 'src="', '"')
                eps = regex_from_to(a, '<div class="episode.*?">', '<')
                if eps =='':
                        if metaset=='true':
                                addDir2('[B][COLOR white]%s[/COLOR][/B]' %name,baseurl+url,3,thumb,items)
                        else:
                                addDir('[B][COLOR white]%s[/COLOR][/B]' %name,baseurl+url,3,thumb,fanart,'')
        try:
                nextp = regex_get_all(link, '<a class="item"', '</a>')
                for a in nextp:
                    url = regex_from_to(a, 'href="', '"').replace("&amp;","&")
                    name = regex_from_to(a, 'title="', '"').replace("&amp;","&").replace('&#39;',"'").replace('&quot;','"').replace('&#039;',"'")
                    if 'Next' in name:
                        addDir('[B][COLOR red]Next Page>>>[/COLOR][/B]',url,1,icon,fanart,'')
                    else:
                        addDir('[B][COLOR red]%s[/COLOR][/B]' %name,url,1,icon,fanart,'')
        except: pass
        setView('movies', 'movie-view')




def INDEX2(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore').decode('ascii')
        all_videos = regex_get_all(link, '<a class="thumb"', '</li>')
        items = len(all_videos)
        for a in all_videos:
                name = regex_from_to(a, 'title="', '"').replace("&amp;","&").replace('&#39;',"'").replace('&quot;','"').replace('&#039;',"'")
                url = regex_from_to(a, 'href="', '"').replace("&amp;","&")
                thumb = regex_from_to(a, 'src="', '"')
                eps = regex_from_to(a, '<div class="episode.*?">', '</')
                eps = eps.replace('<span>',' ')
                if eps > '':
                        addDir('[B][COLOR white]%s [/COLOR][/B][I][COLOR red](%s)[/COLOR][/I]' %(name,eps),baseurl+url,6,thumb,fanart,'')
        try:
                nextp = regex_get_all(link, '<a class="item"', '</a>')
                for a in nextp:
                    url = regex_from_to(a, 'href="', '"').replace("&amp;","&")
                    name = regex_from_to(a, 'title="', '"').replace("&amp;","&").replace('&#39;',"'").replace('&quot;','"').replace('&#039;',"'")
                    if 'Next' in name:
                        addDir('[I][COLOR red]Next Page>>>[/COLOR][/I]',url,2,icon,fanart,'')
                    else:
                        addDir('[I][COLOR red]%s[/COLOR][/I]' %name,url,2,icon,fanart,'')
        except: pass
        setView('movies', 'movie-view')




def EPIS(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore')
        addDir('[B][COLOR white] 01[/COLOR][/B]' ,url,3,iconimage,fanart,'')
        match=re.compile('<li>.*?href="(.*?)" data-id="(.*?)".*?>(.*?)</a></li>').findall(link) 
        for url,data_id,name in match:
                ok = 'film/'
                if ok in url:
                        url = baseurl+url
                        form_data={'hash_id': data_id}
                        headers = {'host': '9movies.to', 'content-type':'application/json, text/javascript, */*; q=0.01',
                                   'referer': url,
                                   'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36','x-requested-with':'XMLHttpRequest'}
                        r = requests.get('http://9movies.to/ajax/film/episode?hash_id='+data_id, data=form_data, headers=headers).text
                        link = re.compile('"videoUrlHash":"(.*?)"').findall(r)[0]
                        link = link.replace('\/','%2F').replace(':','%3A').replace('=','%3D').replace('@','%40')
                        headers['User-Agent'] = User_Agent
                        headers = {}
                        r = requests.get('http://player.9movies.to/grabber/?flash=1&link='+link+'&json=1', data=form_data, headers=headers).text
                        try:
                                url = re.compile('"label":".*?","file":"(.*?)"').findall(r)[-1]
                        except:
                                url = re.compile('"label":".*?","file":"(.*?)"').findall(r)[0]
                        addDir('[B][COLOR white]%s[/COLOR][/B]' %name,url,11,icon,fanart,'')
        setView('movies', 'movie-view')




def LINK(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore')
        data_id = re.compile('data-id="(.*?)"').findall(link)[1]
        url = url+data_id
        form_data={'hash_id': data_id}
        headers = {'host': '9movies.to', 'content-type':'application/json, text/javascript, */*; q=0.01',
                   'referer': url,
                   'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36','x-requested-with':'XMLHttpRequest'}
        r = requests.get('http://9movies.to/ajax/film/episode?hash_id='+data_id, data=form_data, headers=headers).text
        link = re.compile('"videoUrlHash":"(.*?)"').findall(r)[0]
        link = link.replace('\/','%2F').replace(':','%3A').replace('=','%3D').replace('@','%40')
        headers['User-Agent'] = User_Agent
        headers = {}
        r = requests.get('http://player.9movies.to/grabber/?flash=1&link='+link+'&json=1', data=form_data, headers=headers).text
        try:
                url = re.compile('"label":".*?","file":"(.*?)"').findall(r)[-1]
                liz = xbmcgui.ListItem(name, iconImage='DefaultVideo.png', thumbnailImage=iconimage)
                liz.setInfo(type='Video', infoLabels={'Title':description})
                liz.setProperty("IsPlayable","true")
                liz.setPath(url)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
        except:
                url = re.compile('"label":".*?","file":"(.*?)"').findall(r)[0]
                liz = xbmcgui.ListItem(name, iconImage='DefaultVideo.png', thumbnailImage=iconimage)
                liz.setInfo(type='Video', infoLabels={'Title':description})
                liz.setProperty("IsPlayable","true")
                liz.setPath(url)
                xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)




def LINK2(url):
        liz = xbmcgui.ListItem(name, iconImage='DefaultVideo.png', thumbnailImage=iconimage)
        liz.setInfo(type='Video', infoLabels={'Title':description})
        liz.setProperty("IsPlayable","true")
        liz.setPath(url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)




def SEARCH():
        keyb = xbmc.Keyboard('', 'Search')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText().replace(' ','+')
                url = baseurl+'search?keyword='+search
                INDEX(url)




def SEARCH2():
        keyb = xbmc.Keyboard('', 'Search')
        keyb.doModal()
        if (keyb.isConfirmed()):
                search = keyb.getText().replace(' ','+')
                url = baseurl+'search?keyword='+search
                INDEX2(url)




def GENRE(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore')
        match=re.compile('<li><a title="(.*?)" href="(.*?)">.*?</a></li>').findall(link) 
        for name,url in match:
                ok = 'genre'
                if ok in url:
                        addDir('[B][COLOR white]%s[/COLOR][/B]' %name,baseurl+url,1,icon,fanart,'')




def COUNTRY(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore')
        match=re.compile('<a title="(.*?)" href="(.*?)">.*?</a></li>').findall(link) 
        for name,url in match:
                ok = 'country'
                if ok in url:
                        addDir('[B][COLOR white]%s[/COLOR][/B]' %name,baseurl+url,1,icon,fanart,'')




def YEAR(url):
        link = OPEN_URL(url)
        link = link.encode('ascii', 'ignore')
        match=re.compile('<a title="(.*?)" href="(.*?)">.*?</a></li>').findall(link) 
        for name,url in match:
                ok = 'release'
                name = name.replace('release','released')
                if ok in url:
                        addDir('[B][COLOR white]%s[/COLOR][/B]' %name,baseurl+url,1,icon,fanart,'')




def regex_from_to(text, from_string, to_string, excluding=True):
        if excluding:
                try: r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
                except: r = ''
        else:
                try: r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
                except: r = ''
        return r




def regex_get_all(text, start_with, end_with):
        r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
        return r
        


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



def addDir(name,url,mode,iconimage,fanart,description):
        name = name.replace('()','')
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&description="+urllib.quote_plus(description)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name,"Plot":description} )
        liz.setProperty('fanart_image', fanart)
        if mode==3 or mode==11:
            liz.setProperty("IsPlayable","true")
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
        else:
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok




def addDir2(name,url,mode,iconimage,itemcount):
        name = name.replace('[B][COLOR white]','').replace('[/COLOR][/B]','')
        splitName=name.partition('(')
        simplename=""
        simpleyear=""
        if len(splitName)>0:
            simplename=splitName[0]
            simpleyear=splitName[2].partition(')')
        if len(simpleyear)>0:
            simpleyear=simpleyear[0]
        meta = metaget.get_meta('movie',simplename,simpleyear)
        if meta['cover_url']=='':
            try:
                meta['cover_url']=iconimage
            except:
                meta['cover_url']=icon
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&site="+str(site)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage=meta['cover_url'], thumbnailImage=meta['cover_url'])
        liz.setInfo( type="Video", infoLabels= meta )
        contextMenuItems = []
        contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)')),
        liz.addContextMenuItems(contextMenuItems, replaceItems=False)
        if not meta['backdrop_url'] == '': liz.setProperty('fanart_image', meta['backdrop_url'])
        else: liz.setProperty('fanart_image', fanart)
        if mode==3 or mode==11:
            liz.setProperty("IsPlayable","true")
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False,totalItems=itemcount)
        else:
             ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=itemcount)
        return ok




def addLink(name,url,mode,iconimage,fanart,description=''):
        #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+str(description)
        #ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, 'plot': description } )
        liz.setProperty('fanart_image', fanart)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,isFolder=False)
        return ok




def OPEN_URL(url):
    headers = {}
    name = ''
    headers['User-Agent'] = User_Agent
    link = requests.get(url, headers=headers).text
    return link




''' Why recode whats allready written and works well,
    Thanks go to Eldrado for it '''

def setView(content, viewType):
        
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if addon.get_setting('auto-view') == 'true':

        print addon.get_setting(viewType)
        if addon.get_setting(viewType) == 'Info':
            VT = '504'
        elif addon.get_setting(viewType) == 'Info2':
            VT = '503'
        elif addon.get_setting(viewType) == 'Info3':
            VT = '515'
        elif addon.get_setting(viewType) == 'Fanart':
            VT = '508'
        elif addon.get_setting(viewType) == 'Poster Wrap':
            VT = '501'
        elif addon.get_setting(viewType) == 'Big List':
            VT = '51'
        elif viewType == 'default-view':
            VT = addon.get_setting(viewType)

        print viewType
        print VT
        
        xbmc.executebuiltin("Container.SetViewMode(%s)" % ( int(VT) ) )

    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_MPAA_RATING )

           
params=get_params()
url=None
name=None
mode=None
iconimage=None
description=None
site=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:
        description=urllib.unquote_plus(params["description"])
except:
        pass
   
        
if mode==None or url==None or len(url)<1:
        CAT()

elif mode==1:
        INDEX(url)

elif mode==2:
        INDEX2(url)

elif mode==3:
        LINK(url)

elif mode==4:
        SEARCH()

elif mode==5:
        GENRE(url)

elif mode==6:
        EPIS(url)

elif mode==7:
        COUNTRY(url)

elif mode==8:
        YEAR(url)

elif mode==9:
        TV()

elif mode==10:
        SEARCH2()

elif mode==11:
        LINK2(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
