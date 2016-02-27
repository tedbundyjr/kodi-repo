# -*- coding: utf-8 -*-


import re,urlparse
from liveresolver.modules import client

def resolve(url):
    #try:
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url
        result = client.request(url, referer = referer)
        token = re.findall('securetoken\s*:\s*(?:\'|\")(.+?)(?:\'|\")',result)[0]
        rtmp = re.findall('file\s*:\s*(?:\'|\")(.+?)(?:\'|\")',result)[0]
        url = rtmp + ' swfUrl=http://p.jwpcdn.com/6/11/jwplayer.flash.swf live=1 token=' + token + ' timeout=14 swfVfy=1 pageUrl=' + url
        return url
    #except:
     #  return

