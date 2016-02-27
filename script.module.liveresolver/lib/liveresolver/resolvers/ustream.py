# -*- coding: utf-8 -*-



import re,urllib,urlparse,base64
from liveresolver.modules import client

def resolve(url):
    try:
        try:
            referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except:
            referer=url
        page = url
        result = client.request(page, referer=referer)
        id = re.findall('.*ustream.vars.(?:channelId|cId)=([^;]+).*',result)[0]
        url = 'http://iphone-streaming.ustream.tv/uhls/' + id + '/streams/live/iphone/playlist.m3u8'
        return url
    except:
        return


