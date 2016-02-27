# -*- coding: utf-8 -*-


import re,urllib,urlparse,base64
from liveresolver.modules import client, xppod

def resolve(url):
    #try:
        id  = urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0] 
        try:
            referer  = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0] 
        except: referer = url
        pageUrl=url
        
        
        result = client.request(url, referer=referer)
        file = re.findall('.*?file["\'][:,]["\']([^"\']+)["\']',result)[0]
        file = file.replace('OQUl','')
        file = xppod.decode_hls(file)
        url = file + '|Referer=http://cdn-b.streamshell.net/swf/uppod-hls.swf&User-Agent=Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.97 Safari/537.36'
        return url
    #except:
    #    return

