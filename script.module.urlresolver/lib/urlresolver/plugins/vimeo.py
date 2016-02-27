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
import json
from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin

class VimeoResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "vimeo"
    domains = ["vimeo.com"]
    pattern = '(?://|\.)(vimeo\.com)/(?:video/)?([0-9a-zA-Z]+)'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)

        data = self.net.http_GET(web_url).content
        data = json.loads(data)

        vids = data['request']['files']['progressive']
        vids = [i['url'] for i in vids if 'url' in i]

        if vids:
            vUrlsCount = len(vids)

            if (vUrlsCount > 0):
                q = self.get_setting('quality')
                # Lowest Quality
                i = 0

                if q == '1':
                    # Medium Quality
                    i = (int)(vUrlsCount / 2)
                elif q == '2':
                    # Highest Quality
                    i = vUrlsCount - 1

                vUrl = vids[i]
                return vUrl

    def get_url(self, host, media_id):
        return 'http://player.vimeo.com/video/%s/config' % media_id

    def get_host_and_id(self, url):
        r = re.search(self.pattern, url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        return re.search(self.pattern, url) or self.name in host

    #PluginSettings methods
    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting label="Video Quality" id="%s_quality" ' % self.__class__.__name__
        xml += 'type="enum" values="Low|Medium|High" default="2" />\n'
        return xml