#!/usr/bin/python
# (c)AresU, October 8, 2015
# Greetz to: TioEuy & Bosen
# Version:
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

pass#print  "Here in default-py sys.argv =", sys.argv

mainURL="http://www.dramaonline.us"
thisPlugin = int(sys.argv[1])
addonId = "plugin.video.dramaonline"
dataPath = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
#if not path.exists(dataPath):
#       cmd = "mkdir -p " + dataPath
#       system(cmd)
       
Host = "http://www.dramaonline.us"

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
    url="/search?keyword=" + stext.replace(' ','%20')
    ok = showMenu(url)
    #addDirectoryItem(name, {"name":name, "url":url, "mode":3}, pic)
    #xbmcplugin.endOfDirectory(thisPlugin)
                      
def showMainMenu():
    pic = " "
    addDirectoryItem("Most Popular", {"name":"Most Popular", "url":Host, "mode":1}, pic)
    addDirectoryItem("Browse", {"name":"Browse", "url":Host, "mode":2}, pic)
    addDirectoryItem("Search", {"name":"Search", "url":Host, "mode":3}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showLetterList():
    huruf='abcdefghijklmnopqrstuvwxyz'
    pic = ""
    #addDirectoryItem('#', {"name":'#', "url":"/drama-list/char-start-other.html", "mode":21}, pic)
    for i in range(len(huruf)):
        url="/drama-list/char-start-%s.html" % huruf[i]
        addDirectoryItem(huruf[i].upper(), {"name":huruf[i].upper(), "url":url, "mode":21}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showMenu(url):
    url=mainURL+url
    pass#print "GEDEBUG: ",url
    content = getUrl(url)
    pass#print  "content B =", content
    regTxt ='<li class=".*?"> .*? <a href="(.+?)" class="thumbnail" title="(.+?)">.*?<span class="image_intro" style="background\-image\:url\(\'(.+?)\'\)">' #MostPopular
    match = re.split(regTxt,content)
#    pprint(match)
    pic = " "
    for i in range(1,len(match),4):
      #gedebug('url: %s, name: %s, pic: %s' % (url,name,pic))
      url=mainURL+match[i]
      name=match[i+1]
      pic=match[i+2].replace(' ','%20')
      addDirectoryItem(name, {"name":name, "url":url, "mode":11}, pic)
    #addDirectoryItem("Categories", {"name":"Categories", "url":url, "mode":2}, pic)
    #addDirectoryItem("Search", {"name":"Search", "url":Host, "mode":8}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showEpisodes(name1, url):
    print 'GEDEBUG: Name: %s URL: %s' % (name1,url)
    content = getUrl(url)
    regTxt='<a href="(.+?)" class="thumbnail" title="(.+?)">' #Episodes
    match = re.split(regTxt,content)
    pic = " "
    for i in range(1,len(match),3):
      #gedebug('url: %s, episode: %s' % (url,name))
      urlTarget=mainURL+match[i]
      name=match[i+1]
      addDirectoryItem(name, {"name":name, "url":urlTarget, "mode":12}, pic)
    xbmcplugin.endOfDirectory(thisPlugin)

def showQuality(name1, url):
    print 'GEDEBUG: Name: %s URL: %s' % (name1,url)
    content = getUrl(url)
    regTxt='<video id="(.+?)".*?<source src="(.+?)" type=\'(.+?)\'' #Quality
    match = re.compile(regTxt,re.DOTALL).findall(content)
    pic = " "
    for name,urlTarget,type in match:
      gedebug('name: %s, url: %s' % (name,urlTarget))
      addDirectoryItem(name, {"name":name, "url":urlTarget, "mode":13}, pic)
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

#### ACTIONS ####
if not sys.argv[2]:
        pass#print  "Here in default-py going in showContent"
	ok = showMainMenu()
else:
        if mode == str(1): #Click MostPopular
		ok = showMenu("/most-popular.html")
	elif mode == str(2):  #Click Browse
		ok = showLetterList()
	elif mode == str(3):  #Click Search
		ok = showSearch()
	elif mode == str(11):  #Click Episode
		ok = showEpisodes(name, url)
	elif mode == str(12):  #Click quality
		ok = showQuality(name,url)
	elif mode == str(13): #Play video
		ok = playVideo(url)
	elif mode == str(21): #Show List by Letter
		ok = showMenu(url)
