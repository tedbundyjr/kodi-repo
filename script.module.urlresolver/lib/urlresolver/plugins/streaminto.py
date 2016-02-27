"""
    urlresolver XBMC Addon
    Copyright (C) 2011 t0mm0

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import urllib2
from t0mm0.common.net import Net
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class StreamintoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "streaminto"
    domains = ["streamin.to"]
    pattern ='(?://|\.)(streamin\.to)/(?:embed-|)?([0-9A-Za-z]+)'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        html = self.net.http_GET(web_url).content

        try:
            stream_url = re.compile("file\s*:\s*[\'|\"](http.+?)[\'|\"]").findall(html)[0]
            r = urllib2.Request(stream_url, headers={ 'User-Agent': common.IE_USER_AGENT })
            r = urllib2.urlopen(r, timeout=15).headers['Content-Length']
            return stream_url
        except:
            pass

        try:
            streamer = re.search('streamer:\s*"([^"]+)",', html).group(1).replace(':1935', '')
            playpath = re.search('file:\s*"([^"]+)",', html).group(1).replace('.flv', '')
            return '%s playpath=%s' % (streamer, playpath)
        except:
            pass

        raise UrlResolver.ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
            return 'http://streamin.to/embed-%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False
    
    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
