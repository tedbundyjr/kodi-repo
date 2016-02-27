# -*- coding: utf-8 -*-


import re,urlparse,json,urllib
from liveresolver.modules import client,decryptionUtils



def resolve(url):
    try:
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url
        try: id = urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0]
    	except: id = re.findall('streamup.com/(.+?)/embed',url)[0]
        roomSlug = id+'s-stream'
        xurl = "https://lancer.streamup.com/api/channels/" + roomSlug + "/playlists"
        url = json.loads(client.request(xurl))['hls']
        url += '|%s' % urllib.urlencode({'User-Agent': client.agent(), 'Referer': referer})
        return url
    except:
        return


