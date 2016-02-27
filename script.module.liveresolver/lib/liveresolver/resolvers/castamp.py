# -*- coding: utf-8 -*-


import re,urllib,urlparse,base64
from liveresolver.modules import client

def resolve(url):
    try:
        id  = urlparse.parse_qs(urlparse.urlparse(url).query)['c'][0] 
        
        url = 'http://castamp.com/embed.php?c=%s&vwidth=640&vheight=380'%id
        pageUrl=url
        try:
            referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except:
            referer= url 
        
        result = client.request(url, referer=referer)
        swf = re.compile('\'flashplayer\'\s*:\s*(?:\'|\")(.+?)(?:\'|\")').findall(result)[-1]
        file = re.compile('\'file\'\s*:\s*(?:\'|\")(.+?)(?:\'|\")').findall(result)[-1]
        rtmp = re.compile('\'streamer\'\s*:\s*(?:\'|\")(.+?)(?:\'|\")').findall(result)[-1]

        url = rtmp + ' playpath=' + file + ' swfUrl=' + swf + ' live=true timeout=15 swfVfy=1 pageUrl=' + pageUrl
        return url
    
    except:
        return

