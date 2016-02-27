# -*- coding: utf-8 -*-


import re,urllib,urlparse,json,base64
from liveresolver.modules import client

def resolve(url):
    try:
        pageUrl = url
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = url
        url = find_html(url,referer)
        result = client.request(url, referer=pageUrl, headers= { 'Host': urlparse.urlparse(url).netloc} )
        try:
            result = urllib.unquote(result)
        except:
            pass
        
        ssx1 = base64.b64decode(re.findall('id="ssx1" value="(.+?)"',result)[0])
        ssx4 = base64.b64decode(re.findall('id="ssx4" value="(.+?)"',result)[0])
        token = re.findall('securetoken:\s*(.+?)\s*\}',result)[0]
        app = re.findall('.*rtmp://[\.\w:]*/([^"\']+)',ssx4)[0]
        url = ssx4 + ' app=' + app + ' playpath=' + ssx1 + ' swfUrl=ttp://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf live=true flashver=WIN\\2020,0,0,228 token='+ token + ' timeout=15 pageUrl=' + pageUrl
        return url
    except:
        return

def find_html(url, referer):
    try:
        
        result = client.request(url, referer=referer)
        print(result)
        ssx1 = base64.b64decode(re.findall('id="ssx1" value="(.+?)"',result)[0])
        return url
    except:
        try:
            src = re.findall('src="([^"]+)"',result)[0]
            return find_html(src,url)
        except:
            host1 = urlparse.urlparse(url).netloc
            host = re.findall('src=[\'\"]http://(.+?)/player.js',result)[0]
            url2 = url.replace(host1,host)
            return find_html(url2,referer)
