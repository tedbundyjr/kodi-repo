# Config Wizard By: Blazetamer 2013-2014
# Thanks to Blazetamer, TheHighway, and the rest of the crew at TVADDONS.ag (XBMCHUB.com).
import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,os,sys,downloader,extract,time,shutil
import wizardmain as main
AddonTitle='Config Wizard'; wizardUrl='http://tribeca.tvaddons.ag/tools/wizard/'; 
SiteDomain='TVADDONS.AG'; TeamName='TEAM TVADDONS'; 
addon=main.addon; net=main.net; settings=main.settings; 
SkinBackGroundImg=os.path.join('special://','home','media','SKINDEFAULT.jpg')
RequiredHostsPath=xbmc.translatePath(os.path.join(main.AddonPath,'requiredhosts.py'))
RequiredHostsUrl=wizardUrl+'requiredhosts.txt'
RequiredHostsUrl='https://offshoregit.com/xbmchub/config-wizard-development/raw/master/requiredhosts.py'
LinksUrl=wizardUrl+'links.txt'
#LinksUrl='https://offshoregit.com/xbmchub/config-wizard-development/raw/master/links.txt'
LocalLinks=xbmc.translatePath(os.path.join(main.AddonPath,'links.txt'))
#==========================Help WIZARD=====================================================================================================
def HELPCATEGORIES():
    if ((XBMCversion['Ver'] in ['','']) or (int(XBMCversion['two']) < 12)) and (settings.getSetting('bypass-xbmcversion')=='false'):
        eod(); addon.show_ok_dialog(["Compatibility Issue: Outdated Kodi Setup","Please upgrade to a newer version of XBMC first!","Visit %s for Support!"%SiteDomain],title="XBMC "+XBMCversion['Ver'],is_error=False); DoA('Back'); 
    else:
        if main.isFile(LocalLinks)==True: link=main.nolines(main.FileOpen(LocalLinks))
        else: link=main.OPEN_URL(LinksUrl).replace('\n','').replace('\r','').replace('\a','')
        match=re.compile('name="(.+?)".+?rl="(.+?)".+?mg="(.+?)".+?anart="(.+?)".+?escription="(.+?)".+?ype="(.+?)"').findall(link)
        for name,url,iconimage,fanart,description,filetype in match:
            #if 'status' in filetype:
                #main.addHELPDir(name,url,'wizardstatus',iconimage,fanart,description,filetype)
            #else:    
                main.addHELPDir(name,url,'helpwizard',iconimage,fanart,description,filetype)
        CustomUrl=settings.getSetting('custom-url')
        try:
            if (len(CustomUrl) > 10) and ('://' in CustomUrl):
                main.addHELPDir('Custom Url[CR](Addon Settings)',CustomUrl,'helpwizard',main.AddonIcon,main.AddonFanart,"Custom url found in addon settings.","main") ## For Testing to test a url with a FileHost.
        except: pass
        #main.addHELPDir('Testing','http://www.firedrive.com/file/################','helpwizard',iconimage,fanart,description,filetype) ## For Testing to test a url with a FileHost.
        main.AUTO_VIEW('movies')
        ## ### ## 
def xEBb(t): main.xEB('Skin.SetBool(%s)'%t)
def xEBS(t,n): main.xEB('Skin.SetString(%s,%s)'%(t,n))
def HELPWIZARD(name,url,description,filetype):
    path=xbmc.translatePath(os.path.join('special://home','addons','packages')); confirm=xbmcgui.Dialog(); filetype=filetype.lower(); 
    if filetype=='splash':
        try: html=main.OPEN_URL(url)
        except: return
        import splash_highway as splash
        SplashBH=xbmc.translatePath(os.path.join(main.AddonPath,'ContentPanel.png'))
        ExitBH=xbmc.translatePath(os.path.join(main.AddonPath,'Exit.png'))
        splash.do_My_TextSplash2(html,SplashBH,12,TxtColor='0xff00bfff',Font='font12',BorderWidth=40,ImgexitBtn=ExitBH,colorDiffuse='0xff00bfff'); 
        return
    if confirm.yesno(TeamName,"Would you like %s to "%SiteDomain,"customize your add-on selection? "," "):
        dp=xbmcgui.DialogProgress(); dp.create(AddonTitle,"Downloading ",'','Please Wait')
        lib=os.path.join(path,name+'.zip')
        try: os.remove(lib)
        except: pass
        ### ## ... ## 
        #try:
        #    if (main.isFile(LocalLinks)==False) or (main.isFile(RequiredHostsPath)==False): FHTML=main.OPEN_URL(RequiredHostsUrl); main.FileSave(RequiredHostsPath,FHTML); time.sleep(2)
        #except: pass
        if main.isFile(RequiredHostsPath)==False: dialog=xbmcgui.Dialog(); dialog.ok("Error!",'import not found.'); return
        try: import requiredhosts as RequiredHosts
        except: print "error attempting to import requiredhosts as RequiredHosts"; dialog=xbmcgui.Dialog(); dialog.ok("Error!","import failed."); return
        #print {'url':url}
        url=RequiredHosts.CheckForHosts(url); #print {'url':url}
        ### ## ... ## 
        if str(url).endswith('[error]'): print url; dialog=xbmcgui.Dialog(); dialog.ok("Error!",url); return
        if '[error]' in url: print url; dialog=xbmcgui.Dialog(); dialog.ok("Error!",url); return
        if not str(url).lower().startswith('http://'): print url; dialog=xbmcgui.Dialog(); dialog.ok("Error!",url); return
        print {'url':url}
        downloader.download(url,lib,dp)
        ### ## ... ## 
        #return ## For Testing 2 Black Overwrite of stuff. ##
        ### ## ... ## 
        if   filetype=='main':  addonfolder=xbmc.translatePath('special://home')
        elif filetype=='addon': addonfolder=xbmc.translatePath(os.path.join('special://home','addons'))
        else: print {'filetype':filetype}; dialog=xbmcgui.Dialog(); dialog.ok("Error!",'filetype: "%s"'%str(filetype)); return
        #time.sleep(2)
        xbmc.sleep(4000)
        dp.update(0,"","Extracting Zip Please Wait")
        print '======================================='; print addonfolder; print '======================================='
        extract.all(lib,addonfolder,dp)
        proname=xbmc.getInfoLabel("System.ProfileName")
        if (filetype=='main') and (settings.getSetting('homescreen-shortcuts')=='true'):
            link=main.OPEN_URL(wizardUrl+'shortcuts.txt')
            shorts=re.compile('shortcut="(.+?)"').findall(link)
            for shortname in shorts: main.xEB('Skin.SetString(%s)'%shortname)
        if (filetype=='main') and (settings.getSetting('other-skin-settings')=='true'):
            #main.xEB('Skin.SetString(CustomBackgroundPath,%s)' %img)
            #main.xEB('Skin.SetBool(ShowBackgroundVideo)')       ## Set to true so we can later set them to false.
            #main.xEB('Skin.SetBool(ShowBackgroundVis)')         ## Set to true so we can later set them to false.
            #main.xEB('Skin.ToggleSetting(ShowBackgroundVideo)') ## Switching from true to false.
            #main.xEB('Skin.ToggleSetting(ShowBackgroundVis)')   ## Switching from true to false.
            xEBb('HideBackGroundFanart')
            xEBb('HideVisualizationFanart')
            xEBb('AutoScroll')
        if (filetype=='main') and (main.isFile(xbmc.translatePath(SkinBackGroundImg))==True): 
            xEBS('CustomBackgroundPath',SkinBackGroundImg)
            xEBb('UseCustomBackground')
        #time.sleep(2)
        xbmc.sleep(4000)
        xbmc.executebuiltin('UnloadSkin()'); xbmc.executebuiltin('ReloadSkin()'); xbmc.executebuiltin("LoadProfile(%s)" % proname)
        dialog=xbmcgui.Dialog(); dialog.ok("Success!","Installation Complete","   [COLOR gold]Brought To You By %s[/COLOR]"%SiteDomain)
        ##
#==========
def DoA(a): xbmc.executebuiltin("Action(%s)" % a) #DoA('Back'); # to move to previous screen.
def eod(): addon.end_of_directory()
#==========OS Type & XBMC Version===========================================================================================
XBMCversion={}; XBMCversion['All']=xbmc.getInfoLabel("System.BuildVersion"); XBMCversion['Ver']=XBMCversion['All']; XBMCversion['Release']=''; XBMCversion['Date']=''; 
if ('Git:' in XBMCversion['All']) and ('-' in XBMCversion['All']): XBMCversion['Date']=XBMCversion['All'].split('Git:')[1].split('-')[0]
if ' ' in XBMCversion['Ver']: XBMCversion['Ver']=XBMCversion['Ver'].split(' ')[0]
if '-' in XBMCversion['Ver']: XBMCversion['Release']=XBMCversion['Ver'].split('-')[1]; XBMCversion['Ver']=XBMCversion['Ver'].split('-')[0]
if len(XBMCversion['Ver']) > 1: XBMCversion['two']=str(XBMCversion['Ver'][0])+str(XBMCversion['Ver'][1])
else: XBMCversion['two']='00'
if len(XBMCversion['Ver']) > 3: XBMCversion['three']=str(XBMCversion['Ver'][0])+str(XBMCversion['Ver'][1])+str(XBMCversion['Ver'][3])
else: XBMCversion['three']='000'
sOS=str(main.get_xbmc_os()); 
print [['Version All',XBMCversion['All']],['Version Number',XBMCversion['Ver']],['Version Release Name',XBMCversion['Release']],['Version Date',XBMCversion['Date']],['OS',sOS]]
#==========END HELP WIZARD==================================================================================================
params=main.get_params(); url=None; name=None; mode=None; year=None; imdb_id=None
def ParsUQP(s,Default=None):
    try: return urllib.unquote_plus(params[s])
    except: return Default
fanart=ParsUQP("fanart",""); description=ParsUQP("description",""); filetype=ParsUQP("filetype",""); url=ParsUQP("url",""); name=ParsUQP("name",""); mode=ParsUQP("mode"); year=ParsUQP("year"); 
print "Mode: "+str(mode); print "URL: "+str(url); print "Name: "+str(name); print "Year: "+str(year)
if   mode==None or url==None or len(url)<1: HELPCATEGORIES()
elif mode=="wizardstatus": print""+url; items=main.WIZARDSTATUS(url)
elif mode=='helpwizard': HELPWIZARD(name,url,description,filetype)
xbmcplugin.endOfDirectory(int(sys.argv[1]))        
