# -*- coding: utf-8 -*-


import re,urllib,urlparse,base64
from liveresolver.modules import client

def resolve(url):
    try:
    	try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url
        result = client.request(url, referer = referer)
        #file = re.findall('.*?[\'"]*file[\'"]*[:,]\s*[\'"]([^\'"]+).*?',result)[0]
        file = re.findall('.*(http[^"\']+\.m3u8[^"\']*).*',result)[0]
        url = file+'|Referer='+referer+'&User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36&X-Requested-With=ShockwaveFlash/20.0.0.228'
        #url = file + ' swfUrl=http://www.scaleengine.com/embed/6.12/jwplayer.flash.swf flashver=WIN\\2019,0,0,226 live=1 token=#ed%h0#w@1 timeout=14 swfVfy=1 pageUrl=' + url
        return url
    
    except:
        return

