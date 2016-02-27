# -*- coding: utf-8 -*-

'''
    Genesis Add-on
    Copyright (C) 2015 lambda

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
'''


import re,urllib,urlparse,base64,json,socket
from liveresolver.modules import client


def resolve(url):
    try:
        referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]

        page = urlparse.parse_qs(urlparse.urlparse(url).query)['id'][0]
        page = 'http://p2pcast.tv/stream.php?id=%s&live=0&p2p=0&stretching=uniform' % page

        result = client.request(page, referer=referer)

        token = client.request('http://p2pcast.tv/getTok.php', referer=page, headers={'User-Agent': client.agent(), 'X-Requested-With': 'XMLHttpRequest'})
        try: token = json.loads(token)['token']
        except: token = ''
        url = re.compile('murl\s*=\s*[\'|\"](.+?)[\'|\"]').findall(result)[0]
        url = base64.b64decode(url) + token
        url += '|Referer='+page+'&User-Agent=%s&X-Requested-With=ShockwaveFlash/19.0.0.245&Host=%s'%(client.agent(),urlparse.urlparse(url).netloc)

        return url
    except:
        return


def resolve_u(src):
    try:
        parsed_link = urlparse.urlsplit(src)
        tmp_host = parsed_link.netloc.split(':')
        tmp_host[0] = socket.gethostbyname(tmp_host[0])
        tmp_host = ':'.join(tmp_host)
        parsed_link = parsed_link._replace(netloc=tmp_host)
        return parsed_link.geturl()
    except:
        return src