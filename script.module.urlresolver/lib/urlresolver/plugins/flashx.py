"""
    Kodi urlresolver plugin
    Copyright (C) 2014  smokdpi

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
from t0mm0.common.net import Net
from lib import jsunpack
from urlresolver.plugnplay import Plugin
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings

class FlashxResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "flashx"
    domains = ["flashx.tv"]
    pattern = '(?://|\.)(flashx\.tv)/(?:embed-|dl\?)?([0-9a-zA-Z/-]+)'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        html = self.net.http_GET(web_url).content

        r = re.search('href="([^"]+)', html)
        if r:
            web_url = r.group(1)
            html = self.net.http_GET(web_url).content

            try: html = jsunpack.unpack(re.search('(eval\(function.*?)</script>', html, re.DOTALL).group(1))
            except: pass

            best = 0
            best_link = ''

            for stream in re.findall('file\s*:\s*"(http.*?)"\s*,\s*label\s*:\s*"(\d+)', html, re.DOTALL):
                if int(stream[1]) > best:
                    best = int(stream[1])
                    best_link = stream[0]

        if best_link:
            return best_link
        else:
            raise UrlResolver.ResolverError('Unable to resolve Flashx link. Filelink not found.')
        
    def get_url(self, host, media_id):
        return 'http://www.flashx.tv/embed-%s.html' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False
    
    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_auto_pick" type="bool" label="Automatically pick best quality" default="false" visible="true"/>' % (self.__class__.__name__)
        return xml
