# -*- coding: utf-8 -*-


import re,urllib,urlparse,base64
from liveresolver.modules import client

def resolve(url):
    try:
    	try:
            referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
     	except:
            referer=url
        result = client.request(url, referer = referer)
        
        pageUrl = re.findall('.*?iframe\s*src=["\']([^"\']+)["\'].*',result)[0]
        result = client.request(pageUrl, referer = referer)
        print(result)
        rtmp = re.findall('.*file\w+\s*[:=]\s*"([^\'",]+).*',result)[0].replace(' ','')
        url = rtmp + ' swfUrl=http://direct-stream.biz/jwplayer/jwplayer.flash.swf flashver=WIN\2020,0,0,267 live=1 timeout=14 swfVfy=1 pageUrl=' + pageUrl
        return url
    
    except:
        return

