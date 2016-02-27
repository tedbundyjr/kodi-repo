'''
Nosvideo urlresolver plugin
Copyright (C) 2013 Vinnydude

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import re
import base64
import urllib
from t0mm0.common.net import Net
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class NosvideoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "nosvideo"
    domains = ["nosvideo.com", "noslocker.com"]
    pattern = '(?://|\.)(nosvideo.com|noslocker.com)/(?:\?v\=|embed/|.+?\u=)?([0-9a-zA-Z]+)'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        if 'File Not Found' in html:
            raise UrlResolver.ResolverError('File Not Found')

        r = re.search('class\s*=\s*[\'|\"]btn.+?[\'|\"]\s+href\s*=\s*[\'|\"](.+?)[\'|\"]', html)
        if not r:
            raise UrlResolver.ResolverError('File Not Found')

        headers = { 'Referer': r.group(1) }

        web_url = 'http://nosvideo.com/vj/video.php?u=%s&w=&h=530' % media_id

        html = self.net.http_GET(web_url, headers=headers).content

        stream_url = re.compile('var\stracker\s*=\s*[\'|\"](.+?)[\'|\"]').findall(html)
        stream_url += re.compile("tracker *: *[\'|\"](.+?)[\'|\"]").findall(html)

        if len(stream_url) > 0:
            stream_url = stream_url[0]
        else:
            raise UrlResolver.ResolverError('Unable to locate video file')

        try: stream_url = base64.b64decode(stream_url)
        except: pass

        stream_url += '|' + urllib.urlencode({ 'User-Agent': common.IE_USER_AGENT })

        return stream_url
 
    def get_url(self, host, media_id):
        return 'http://nosvideo.com/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False
    
    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
