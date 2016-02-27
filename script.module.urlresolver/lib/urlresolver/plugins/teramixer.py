# -*- coding: utf-8 -*-

"""
Teramixer.com urlresolver XBMC Addon
Copyright (C) 2014 JUL1EN094 

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
"""

import re
import base64
import urllib
from t0mm0.common.net import Net
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class TeramixerResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "teramixer"
    domains = [ 'teramixer.com' ]
    pattern ='(?://|\.)(teramixer\.com)/(?:embed/|)?([0-9A-Za-z]+)'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        try:
            web_url = self.get_url(host, media_id)

            html = self.net.http_GET(web_url).content

            url = re.findall("""filepath = '(.*)';""", html)[0]
            url = url[9:]
            url = base64.b64decode(url)
            if not url.startswith('aws'): url = url[1:]

            stream_url = 'http://%s' % url + '|' + urllib.urlencode({ 'User-Agent': common.IE_USER_AGENT })
            return stream_url
        except IndexError as e:
            if re.search("""<title>File not found or deleted - Teramixer</title>""", html) :
                raise UrlResolver.ResolverError('File not found or removed')
            else:
                raise UrlResolver.ResolverError(e)

    def get_url(self, host, media_id):
        return 'http://www.teramixer.com/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False
    
    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
