"""
    urlresolver XBMC Addon
    Copyright (C) 2011 anilkuj

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
from urlresolver import common
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class VeohResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "veoh"
    domains = ["veoh.com"]
    pattern = '(?://|\.)(veoh\.com)/(?:watch/|.+?permalinkId=)?([0-9a-zA-Z/]+)'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        html = self.net.http_GET("http://www.veoh.com/iphone/views/watch.php?id=" + media_id + "&__async=true&__source=waBrowse").content
        if not re.search('This video is not available on mobile', html):
            r = re.compile("watchNow\('(.+?)'").findall(html)
            if (len(r) > 0):
                return r[0]

        url = 'http://www.veoh.com/rest/video/'+media_id+'/details'
        html = self.net.http_GET(url).content
        file = re.compile('fullPreviewHashPath="(.+?)"').findall(html)

        if len(file) == 0:
            raise UrlResolver.ResolverError('File Not Found or removed')

        return file[0]

    def get_url(self, host, media_id):
        return 'http://veoh.com/watch/%s' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host
