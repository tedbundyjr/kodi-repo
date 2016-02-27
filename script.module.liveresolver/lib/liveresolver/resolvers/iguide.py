# -*- coding: utf-8 -*-


import re,urlparse,json
from liveresolver.modules import client


def resolve(url):
    try:
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url

        try:
            channel = urlparse.parse_qs(urlparse.urlparse(url).query)['channel'][0]
        except:
            channel = re.compile('/embed/(\d+)&').findall(url)[0]

        page = 'http://www.iguide.to/embedplayer_new.php?width=640&height=480&channel=%s&autoplay=true' % channel

        result = client.request(page, referer=referer)
        token_url =re.compile('\$.getJSON\("(.+?)", function\(json\){').findall(result)[0]
        token = json.loads(client.request(token_url, referer=referer))['token']

        file = re.compile('(?:\'|\")?file(?:\'|\")?\s*:\s*(?:\'|\")(.+?)(?:\'|\")').findall(result)[0].replace('.flv','')
        rtmp = re.compile('(?:\'|\")?streamer(?:\'|\")?\s*:\s*(?:\'|\")(.+?)(?:\'|\")').findall(result)[0].replace(r'\\','\\').replace(r'\/','/')
        app = re.compile('.*.*rtmp://[\.\w:]*/([^\s]+)').findall(rtmp)[0]

        url=rtmp +  ' playpath=' + file + ' swfUrl=http://www.iguide.to/player/secure_player_iguide_token.swf flashver=WIN\\2020,0,0,228 live=1 timeout=15 token=' + token + ' swfVfy=1 pageUrl='+page
        return url
    except:
        return


