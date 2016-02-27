"""
    urlresolver XBMC Addon
    Copyright (C) 2013 Bstrdsmkr

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

from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import SiteAuth
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
from t0mm0.common.net import Net
import urlparse
import urllib
import time

class SimplyDebridResolver(Plugin, UrlResolver, SiteAuth, PluginSettings):
    implements = [UrlResolver, SiteAuth, PluginSettings]
    name = "Simply-Debrid"
    domains = ["*"]
    base_url = 'https://simply-debrid.com/api.php?'

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.hosts = []
        self.patterns = []
        self.priority = int(p)
        self.net = Net()
        self.username = self.get_setting('username')
        self.password = self.get_setting('password')

    def get_media_url(self, host, media_id):
        query = urllib.urlencode({'dl': media_id})
        url = self.base_url + query
        try:
            response = self.net.http_GET(url).content
            if response:
                common.addon.log_debug('Simply-Debrid: Resolved to %s' % (response))
                if response.startswith('http'):
                    return response
                else:
                    raise UrlResolver.ResolverError('Unusable Response from SD')
            else:
                raise UrlResolver.ResolverError('Null Response from SD')
        except Exception as e:
            raise UrlResolver.ResolverError('Link Not Found: Exception: %s' % (e))

    def login(self):
        try: last_login = int(self.get_setting('last_login'))
        except: last_login = 0
        now = time.time()
        if last_login < (now - (24 * 60 * 60)):
            query = urllib.urlencode({'login': 1, 'u': self.username, 'p': self.password})
            url = self.base_url + query
            response = self.net.http_GET(url).content
            if not response.startswith('02'):
                raise UrlResolver.ResolverError('Simply-Debrid Login Failed: %s' % (response))
            else:
                common.addon.log_debug('SD Login - Success: %s' % (now))
                self.set_setting('last_login', str(int(now)))
        else:
            common.addon.log_debug('Skipping Login - logged in age: %ds' % (now - last_login))
    
    def get_url(self, host, media_id):
        return media_id

    def get_host_and_id(self, url):
        return 'simply-debrid.com', url

    def get_all_hosters(self):
        try:
            if not self.hosts:
                query = urllib.urlencode({'list': 1})
                url = self.base_url + query
                response = self.net.http_GET(url).content
                self.hosts = [host for host in response.split(';') if host]
                common.addon.log_debug('SD Hosts: %s' % (self.hosts))
        except Exception as e:
            common.addon.log_error('Error getting Simply-Debrid hosts: %s' % (e))

    def valid_url(self, url, host):
        if self.get_setting('login') == 'false': return False
        self.get_all_hosters()
        if url:
            try: host = urlparse.urlparse(url).hostname
            except: host = 'unknown'
        if host.startswith('www.'): host = host.replace('www.', '')
        if any(host in item for item in self.hosts):
            return True

        return False

    def get_settings_xml(self):
        xml = PluginSettings.get_settings_xml(self)
        xml += '<setting id="%s_last_login" type="number" visible="false" default="0"/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_login" type="bool" label="login" default="false"/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_username" enable="eq(-1,true)" type="text" label="Username" default=""/>\n' % (self.__class__.__name__)
        xml += '<setting id="%s_password" enable="eq(-2,true)" type="text" label="Password" option="hidden" default=""/>\n' % (self.__class__.__name__)
        return xml

    def isUniversal(self):
        return True
