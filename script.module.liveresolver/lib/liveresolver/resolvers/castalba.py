# -*- coding: utf-8 -*-


import re,urllib,urlparse,base64
from liveresolver.modules import client
from liveresolver.modules.log_utils import log

def resolve(url):
    try:
        try:
            cid  = urlparse.parse_qs(urlparse.urlparse(url).query)['cid'][0] 
        except:
            cid = re.compile('channel/(.+?)(?:/|$)').findall(url)[0]

        
        try:
            referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except:
            referer='http://castalba.tv'
        
        url = 'http://castalba.tv/embed.php?cid=%s&wh=600&ht=380&r=%s'%(cid,urlparse.urlparse(referer).netloc)
        pageUrl=url

        result = client.request(url, referer=referer)
        result=urllib.unquote(result)
        if 'm3u8' in result:
            url = re.compile('filez\s*=\s*(?:unescape\()\'(.+?)\'').findall(result)[0]
            url = 'http://' + url + '.m3u8'
            url += '|%s' % urllib.urlencode({'User-Agent': client.agent(), 'Referer': referer})
            log("Castalba: Found m3u8 url: " + url)
            
        else:
            try:
                filePath = re.compile("'file'\s*:\s*(?:unescape\()?'(.+?)'").findall(result)[0]
                
            except:
                file = re.findall('var file\s*=\s*(?:unescape\()?(?:\'|\")(.+?)(?:\'|\")',result)[0]
                try:
                    file2 = re.findall("'file':\s*unescape\(file\)\s*\+\s*unescape\('(.+?)'\)",result)[0]
                    filePath = file+file2
                except:
                    filePath = file
                
            swf = re.compile("'flashplayer'\s*:\s*\"(.+?)\"").findall(result)[0]
            try:
                streamer=re.findall('streamer\(\)\s*\{\s*return \'(.+?)\';\s*\}',result)[0]
                if 'rtmp' not in streamer:
                    streamer = 'rtmp://' + streamer
            except:
                try:
                    streamer = re.compile("var sts\s*=\s*'(.+?)'").findall(result)[0]
                except:
                    streamer=re.findall('streamer\(\)\s*\{\s*return \'(.+?)\';\s*\}',result)[0]
              
            url = streamer.replace('///','//') + ' playpath=' + filePath +' swfUrl=' + swf + ' flashver=WIN\\2020,0,0,228 live=true timeout=15 swfVfy=true pageUrl=' + pageUrl
            log("Castalba: Found rtmp link: " + url)

        return url
    
    except:
        log("Castalba: Resolver failed. Returning...")
        return

