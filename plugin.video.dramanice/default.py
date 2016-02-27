#!/usr/bin/python
# (c)AresU, October 8, 2015
# Greetz to: TioEuy & Bosen
# Version:
# 20160207: 1.4: Add more stream source
# 20160120: 1.3: Change domain
# 20151205: 1.2: Code cleanup
# 20151017: 1.1: Improve Performance & Show FanArt
# 20151013: 1.0: First release

import xbmc,xbmcplugin
import xbmcgui
import sys
import urllib, urllib2
import time
import re
from htmlentitydefs import name2codepoint as n2cp
import httplib
import urlparse
from os import path, system
import socket
from urllib2 import Request, URLError, urlopen
from urlparse import parse_qs
from urllib import unquote_plus
import xbmcaddon

pass#print  "Here in default-py sys.argv =", sys.argv

mainURL="http://dramanice.to"
thisPlugin = int(sys.argv[1])
addonId = "plugin.video.dramanice"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
addon = xbmcaddon.Addon()
path = addon.getAddonInfo('path')
#if not path.exists(dataPath):
#       cmd = "mkdir -p " + dataPath
#       system(cmd)
     
Host = "http://www.dramanice.to"

def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link
    
def playVideo(url):
    player = xbmc.Player()
    player.play(url)

def gedebug(strTxt):
    print '### GEDEBUG: ' + str(strTxt)
    return
    
def addSearch():
    searchStr = ''
    keyboard = xbmc.Keyboard(searchStr, 'Search')
    keyboard.doModal()
    if (keyboard.isConfirmed()==False):
      return
    searchStr=keyboard.getText()
    if len(searchStr) == 0:
      return
    else:
      return searchStr 

def showSearch():
    pic = " "
    stext = addSearch()
    name = stext
    try:
      url="/search?keyword=" + stext.replace(' ','%20')
      ok = showMenu(url, '1')
    except:
      pass
    #addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
    #xbmcplugin.endOfDirectory(thisPlugin)
                      
def showMainMenu():
    pic = " "
    addDirectoryItem("Search...", {"name":"Search", "url":Host, "mode":99}, pic)
    addDirectoryItem("Most Popular", {"name":"Most Popular", "url":Host, "mode":1}, pic)
    addDirectoryItem("Drama Show", {"name":"Drama Show", "url":Host, "mode":2}, pic)
    addDirectoryItem("Drama Movie", {"name":"Drama Movie", "url":Host, "mode":3}, pic)
    addDirectoryItem("Drama List", {"name":"Drama List", "url":Host, "mode":4}, pic)
    # addDirectoryItem("Browse", {"name":"Browse", "url":Host, "mode":2}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showLetterList(url, category):
    alpha='#abcdefghijklmnopqrstuvwxyz'
    pic = ""
    for i in range(len(alpha)):
      if alpha[i] == '#': huruf = 'other'
      else: huruf = alpha[i].upper()
      addDirectoryItem(alpha[i].upper(), {"name":huruf, "url":url, "mode":22, "category":category, "letter":huruf}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showDramaList(url, category, letter):
    content = getUrl(url)
    if letter == 'other': symbol = '#'
    else: symbol = letter
    regTxt0 = '<div class=[\'"]group-'+letter+' group-all[\'"]>\n*\s*<div class=[\'"]label_nice[\'"]>\n*\s*'+symbol+'\n*\s*</div>\n*\s*(.*?)\n*\s*<div class=\'clearfix paddbot10\'>'
    
    match0 = re.compile(regTxt0,re.DOTALL).findall(content)[0]
    regTxt = '<div.*?country-'+category+'.*?>\n*\s*<a href="(.+?)">(.+?)</a>\n*\s*</div>'
    match = re.compile(regTxt,re.DOTALL).findall(match0)

    pic = ''

    progress = xbmcgui.DialogProgress()
    progress.create('Progress', 'Please wait while we grab all data.')
    i = 0
    l = len(match)
    intl = str(l)+'.0'

    for url, title in match:
      percent = int( ( i / float(intl) ) * 100)
      message = "Drama found : " + str(i) + " out of "+str(l)
      progress.update( percent, "", message, "" )
      
      xbmc.sleep( 1000 )
      if progress.iscanceled():
        break
      i = i + 1
      content = getUrl(url)
      # gedebug(content)
      regEx = '<div class="col-md-5">\n*\s*<div class="thumbnail-big img-intro img-circle" style="background-image: url\(\'(.*?)\'\)"></div>'
      pic = re.compile(regEx,re.DOTALL).findall(content)[0]
      pic = pic.replace(' ','%20')
      addDirectoryItem(title, {"name":title, "url":url, "mode":11}, pic)

    progress.close()

    xbmcplugin.endOfDirectory(thisPlugin)

def nextMenu(url, search):
    u = re.split('[?=]',url)

    if not search: # http://www.dramanice.us/search/a?page=2
      url = u[0]+'?page='
    else: # http://www.dramanice.us/search?keyword=a
      url = u[0]+'/'+u[2]+'?page='

    if len(u) > 1 and not search:
      page = int(u[2])+1
      # gedebug(page)
    else:
      page = 2

    data = {'urlPage':url, 'page':str(page)}
    return data


def showMenu(url, search=''):
    data = nextMenu(url, search)   
    page = data['page']
    urlNext = data['urlPage']+page
    # gedebug(urlNext)

    url=mainURL+url

    pass#print "GEDEBUG: ",url
    content = getUrl(url)
    # gedebug(content)
    pass#print  "content B =", content
    regTxt ='<div class="thumbnail-drama" style="background: url\(\'(.+?)\'\);"></div>\n.*?</a>\n.*?<div class="info-name">\n.*?<a href="(.+?)"><span>(.+?)</span>' #MostPopular
    match = re.split(regTxt,content)
#    pprint(match)
    pic = " "
    picNext = path+"/next.jpg"
    for i in range(1,len(match),4):
      url=mainURL+match[i+1]
      name=match[i+2].replace('&amp;','&').replace('&#39;','\'')
      pic=match[i].replace(' ','%20')
      addDirectoryItem(name, {"name":name, "url":url, "mode":11}, pic)

    addDirectoryItem("Next", {"name":"Next", "url":urlNext, "mode":111, "page":page}, picNext)
    xbmcplugin.endOfDirectory(thisPlugin)

def showCategory(url):
    url=mainURL+url
    content = getUrl(url)
    regTxt0='<div class="filter-category">\n*\s*<ul>\n*\s*(.+?)\n*\s*</ul>'
    regTxt1='<a href="#" data-filter="(.+?)">(.+?)</a>'
    match0 = re.compile(regTxt0,re.DOTALL).findall(content)[0]
    match = re.compile(regTxt1,re.DOTALL).findall(match0)
    pic = " "
    u = ''
    for category, title in match:
      mv = re.compile('.*?-(.+)',re.DOTALL).findall(url)
      if mv[0] == 'movies': 
        u = 'm'
        title = title.replace('DRAMA', 'MOVIE')
      addDirectoryItem(title, {"name":title, "url":url, "mode":21, "category":category}, pic)
    if u == 'm':
      addDirectoryItem('OTHER ASIA MOVIE', {"name":'OTHER', "url":url, "mode":21, "category":'other'}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showEpisodes(name1, url):
    content = getUrl(url)
    regTxt='<a href="(.+?)"><span class="icon-play SUB"></span><span>(.+?)</span>' #Episodes
    match = re.split(regTxt,content)
    pic = " "
    for i in range(1,len(match),3):
      urlTarget=match[i]
      name=match[i+1]
      addDirectoryItem(name, {"name":name, "url":urlTarget, "mode":12}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showQuality(name1, url):
    content = getUrl(url)
    try:
      regTxt='<source src="(.+?)" type="(.+?)" data-res="(.+?)" />' #Quality
      match = re.compile(regTxt,re.DOTALL).findall(content)
      pic = " "
      for urlTarget,type,name in match:
        addDirectoryItem(name, {"name":name, "url":urlTarget, "mode":13}, pic)
    
    except:
      pass

    try:
      regex = 'load_server_drive.*?iframe.*?src="(.*?)".*?>'
      url = re.compile(regex, re.DOTALL).findall(content)[0]

      content = getUrl(url)

      regex = 'file:.*?\'(.+?)\'.*?label:.*?\'(.+?)\''
      match = re.compile(regex, re.DOTALL).findall(content)

      for urlTarget, name in match:
        if name != 'Auto':
          name = re.sub(r'p','',name)
          addDirectoryItem(name, {"name":name, "url":urlTarget, "mode":13}, pic)
    
    except:
      pass

    xbmcplugin.endOfDirectory(thisPlugin)

std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}  

def addDirectoryItem(name, parameters={},pic=""):
    li = xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=pic)
    li.setInfo( "video", { "Title" : name, "FileName" : name} )
    li.setProperty('Fanart_Image', pic)
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=True)


def parameters_string_to_dict(parameters):
    ''' Convert parameters encoded in a URL to a dict. '''
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

params = parameters_string_to_dict(sys.argv[2])
name =  str(params.get("name", ""))
url =  str(params.get("url", ""))
url = urllib.unquote(url)
mode =  str(params.get("mode", ""))
page =  str(params.get("page", ""))
category =  str(params.get("category", ""))
letter =  str(params.get("letter", ""))

#### ACTIONS ####
if not sys.argv[2]:
    pass#print  "Here in default-py going in showContent"
    ok = showMainMenu()
else:
    if mode == str(1): #Click MostPopular #ok = showMenu("/most-popular-drama") #ok = showMenu("/most-popular.html")
        ok = showMenu("/most-popular-drama")
    elif mode == str(2):  #Click Drama Show
        ok = showCategory("/drama-show")
    elif mode == str(21):  #Click Category
        ok = showLetterList(url, category)
    elif mode == str(3):  #Click Drama Movie
        ok = showCategory("/drama-movies")
    elif mode == str(22):  #Click Letter
        ok = showDramaList(url, category, letter)
    elif mode == str(4):  #Click Drama Other
        ok = showLetterList(Host+"/list-all-drama", 'all')    
    # elif mode == str(2):  #Click Browse
    #     ok = showLetterList()
    elif mode == str(99):  #Click Search
        ok = showSearch()
    elif mode == str(11):  #Click Episode
        ok = showEpisodes(name, url)
    elif mode == str(12):  #Click quality
        ok = showQuality(name,url)
    elif mode == str(13): #Play video
        ok = playVideo(url)
    # elif mode == str(21): #Show List by Letter
    #     ok = showMenu(url)
    elif mode == str(111): #Show Next Page
        ok = showMenu(url)
