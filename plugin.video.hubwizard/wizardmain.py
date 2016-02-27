# -*- coding: cp1252 -*-
# Main Module by: Blazetamer and TheHighway
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmc,os,xbmcaddon
try:        from addon.common.addon import Addon
except:
    try:    from t0mm0.common.addon import Addon
    except: from t0mm0_common_addon import Addon
try:        from addon.common.net   import Net
except:
    try:    from t0mm0.common.net   import Net
    except: from t0mm0_common_net   import Net
#Define common.addon
addon_id='plugin.video.hubwizard'; 
AddonTitle='Config Wizard'; 
# Global Stuff
addon=Addon(addon_id,sys.argv); net=Net(); settings=xbmcaddon.Addon(id=addon_id); net.set_user_agent('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'); 
AddonIcon=settings.getAddonInfo('icon')
AddonFanart=settings.getAddonInfo('fanart')
AddonPath=settings.getAddonInfo('path')
# #
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]; cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&'); param={}
                for i in range(len(pairsofparams)):
                        splitparams={}; splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
        return param
def get_xbmc_os():
	try: xbmc_os=str(os.environ.get('OS'))
	except:
		try: xbmc_os=str(sys.platform)
		except: xbmc_os="unknown"
	return xbmc_os
def WIZARDSTATUS(url):
    link=OPEN_URL(url).replace('\n','').replace('\r','').replace('\a','').replace('\t','')
    match=re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)".+?ype="(.+?)"').findall(link)
    for name,url,iconimage,fanart,description,filetype in match: header="[B][COLOR gold]"+name+"[/B][/COLOR]"; msg=(description); TextBoxes(header,msg)
def TextBoxes(heading,anounce):
    class TextBox():
        WINDOW=10147; CONTROL_LABEL=1; CONTROL_TEXTBOX=5
        def __init__(self,*args,**kwargs):
            xbmc.executebuiltin("ActivateWindow(%d)" % (self.WINDOW, )) # activate the text viewer window
            self.win=xbmcgui.Window(self.WINDOW) # get window
            xbmc.sleep(500) # give window time to initialize
            self.setControls()
        def setControls(self):
            self.win.getControl(self.CONTROL_LABEL).setLabel(heading) # set heading
            try: f=open(anounce); text=f.read()
            except: text=anounce
            self.win.getControl(self.CONTROL_TEXTBOX).setText(str(text))
            return
    TextBox()
def nolines(t):
	it=t.splitlines(); t=''
	for L in it: t=t+L
	t=((t.replace("\r","")).replace("\n","").replace("\a",""))
	return t
def isFile(filename): return os.path.isfile(filename)
def FileSave(path,data): file=open(path,'w'); file.write(data); file.close()
def FileOpen(path,Default=''):
	if os.path.isfile(path): file=open(path,'r'); contents=file.read(); file.close(); return contents ## File found.
	else: return Default ## File not found.
def OPEN_URL(url): req=urllib2.Request(url); req.add_header('User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'); response=urllib2.urlopen(req); link=response.read(); response.close(); return link
def xEB(t): xbmc.executebuiltin(t)
def SuggestButton(msg): addon.show_ok_dialog(["By the looks of your operating system","we suggest clicking: ",""+msg],title="OS: "+sOS,is_error=False); 

# HELPDIR
def addHELPDir(name,url,mode,iconimage,fanart,description,filetype): u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&fanart="+urllib.quote_plus(fanart)+"&description="+urllib.quote_plus(description)+"&filetype="+urllib.quote_plus(filetype); ok=True; liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage); liz.setInfo(type="Video",infoLabels={"title":name,"Plot":description}); liz.setProperty("Fanart_Image",fanart); ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False); return ok
# Standard addDir
def addDir(name,url,mode,thumb,labels,favtype):
	contextMenuItems=[]; sitethumb=thumb; sitename=name
	try: name=data['title']; thumb=data['cover_url']; fanart=data['backdrop_url']
	except: name=sitename
	if thumb=='': thumb=sitethumb
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
	ok=True; liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png",thumbnailImage=thumb); liz.setInfo(type="Video",infoLabels=labels)
	if   favtype == 'movie':   contextMenuItems.append(('Movie Information','XBMC.Action(Info)'))
	elif favtype == 'tvshow':  contextMenuItems.append(('TV Show  Information','XBMC.Action(Info)'))
	elif favtype == 'episode': contextMenuItems.append(('TV Show  Information','XBMC.Action(Info)'))       
	liz.addContextMenuItems(contextMenuItems, replaceItems=False)
	try: liz.setProperty("Fanart_Image",labels['backdrop_url'])
	except: pass
	ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True); return ok
# Set View
def doSetView(s): xbmc.executebuiltin("Container.SetViewMode(%s)" % settings.getSetting(s))
# AutoView
def AUTO_VIEW(content):
	if content:
		xbmcplugin.setContent(int(sys.argv[1]),content)
		if settings.getSetting('auto-view')=='true':
			if content=='movies': doSetView('movies-view')
			elif content=='list': doSetView('default-view')
			else: doSetView('default-view')
		else:   doSetView('default-view')
