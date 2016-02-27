# -*- coding: utf-8 -*-


import re,urllib,urlparse
from liveresolver.modules import client

def resolve(url):
    #try:
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
    	except: referer = url
        result = client.request(url, referer=referer)
        url = re.findall('src=(?:\'|\")(.+?\.m3u8)(?:\'|\")',result)[0]
        
        return url
    #except:
     #   return

