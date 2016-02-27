# -*- coding: utf-8 -*-


import re,urlparse
from liveresolver.modules import client

def resolve(url):
    #try:
        try:
            referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except:
            referer=url
    
        result = client.request(url, referer=referer)
        print(result)
        rtmp = re.findall('.*?[\'"]?file[\'"]?[:,]\s*[\'"]([^\'"]+)[\'"].*',result)[0]
        url = rtmp+' swfUrl=http://sostart.org/jw/jwplayer.flash.swf flashver=WIN\2019,0,0,226 token=SECURET0KEN#yw%.?()@W! live=1 timeout=14 swfVfy=1 pageUrl='+url
        return url
    #except:
     # return

