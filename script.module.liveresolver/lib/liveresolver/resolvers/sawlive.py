# -*- coding: utf-8 -*-
import re,urllib,urlparse,base64
from liveresolver.modules import client,decryptionUtils
from liveresolver.modules import jsunpack
from liveresolver.modules.log_utils import log




def resolve(url):
    try:

        page = re.compile('//(.+?)/(?:embed|v)/([0-9a-zA-Z-_]+)').findall(url)[0]
        page = 'http://%s/embed/%s' % (page[0], page[1])
        try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        except: referer = page
        try: host = urlparse.parse_qs(urlparse.urlparse(url).query)['host'][0]
        except: host = 'sawlive.tv'

        headers={'User-Agent': client.agent(),'Host': host, 'Referer': referer, 'Connection': 'keep-alive'}
        
        result = client.request(page, referer=referer)
        
        result = decryptionUtils.doDemystify(result)
        url = client.parseDOM(result, 'iframe', ret='src')[-1]
        url = url.replace(' ', '').replace('+','')
        var = re.compile('var\s(.+?)\s*=\s*[\'\"](.+?)[\'\"]').findall(result)
        for i in range(100):
            for v in var: result = result.replace(" %s " % v[0], ' %s '%v[1])
        var = re.compile('var\s(.+?)\s*=\s*[\'\"](.+?)[\'\"]').findall(result)
        var_dict = dict(var)
        for v in var:
            if '+' in v[1]:
                ss = v[1].rstrip('+').replace('"+','').split('+')
                sg = v[1].rstrip('+').replace('"+','')
                for s in ss:
                    sg = sg.replace(s, var_dict[s])
                var_dict[v[0]]=sg.replace('+','')
        for i in range(100):
            for v in var_dict.keys(): url = url.replace("'%s'" % v, var_dict[v])
            for v in var_dict.keys(): url = url.replace("(%s)" % v, "(%s)" % var_dict[v])
        
        
        result = client.request(url, headers = headers)
        result = decryptionUtils.doDemystify(result)
        
        file = re.compile("'file'.+?'(.+?)'").findall(result)[0]
        log("Sawlive: Found file url: " + file)
        try:
            log("Sawlive: Finding m3u8 link.")
            if not file.startswith('http'): raise Exception()
            url = client.request(file, output='geturl')
            if not '.m3u8' in url: raise Exception()
            url += '|%s' % urllib.urlencode({'User-Agent': client.agent(), 'Referer': file})
            log("Sawlive: Found m3u8 link: " + url)
            return url
        except:
            log("Sawlive: m3u8 link not found, finding rtmp.")
            pass

        strm = re.compile("'streamer'.+?'(.+?)'").findall(result)[0]
        swf = re.compile("SWFObject\('(.+?)'").findall(result)[0]

        url = '%s playpath=%s swfUrl=%s pageUrl=%s live=1 timeout=30' % (strm, file, swf, url)
        url = urllib.unquote(url)
        log("Sawlive: rtmp link found: " + url)
        return url
    except Exception as e:
        log("Sawlive exception:\n" + str(e))
        log("Sawlive: Resolver failed. Returning...")
        return


