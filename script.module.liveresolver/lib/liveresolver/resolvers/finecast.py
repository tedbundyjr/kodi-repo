# -*- coding: utf-8 -*-


import re,urlparse,urllib, cookielib, pickle, requests
from liveresolver.modules import client,unCaptcha
from liveresolver.modules import jsunpack,decryptionUtils

def resolve(url):
    try:
        try:
            referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except:
            referer=url


        id = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
        url = 'http://www.finecast.tv/embed4.php?u=%s&vw=640&vh=450'%id
        headers=[("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0"),
                 ("Referer", referer)]


        cj = cookielib.LWPCookieJar()
        result = unCaptcha.performCaptcha(url, cj, headers = headers)
        file = re.findall('[\'\"](.+?.stream)[\'\"]',result)[0]
        auth = re.findall('[\'\"](\?wmsAuthSign.+?)[\'\"]',result)[0]
        rtmp = 'rtmp://play.finecast.tv:1935/live%s'%auth
        url = rtmp +  ' playpath=' + file + ' swfUrl=http://www.finecast.tv/player6/jwplayer.flash.swf flashver=WIN\2020,0,0,267 live=1 timeout=14 pageUrl=' + url
        return url

        
    except:
        return

