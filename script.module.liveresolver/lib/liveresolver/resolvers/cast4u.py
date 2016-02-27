# -*- coding: utf-8 -*-


import re,urlparse
from liveresolver.modules import client

def resolve(url):
    try:
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url
        result = client.request(url, referer = referer)
        streamer = re.findall(".*?['\"]?file\w*['\"]?\s*[:,=]\s*['\"]([^'\"]+)['\"].*?",result)[0]
        url = streamer + ' swfUrl=http://cast4u.tv/jwplayer/jwplayer.flash.swf flashver=WIN\\2020,0,0,286 live=1 timeout=14 swfVfy=1 pageUrl=' + url
        return url
    except:
        return

