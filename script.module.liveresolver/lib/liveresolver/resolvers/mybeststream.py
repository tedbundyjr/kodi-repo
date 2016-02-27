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


import re,urlparse
from liveresolver.modules import client,decryptionUtils


def resolve(url):
    try:
        referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
        page = url.replace(referer, '').replace('&referer=', '').replace('referer=', '')

        result = client.request(url, referer=referer)
        result = decryptionUtils.doDemystify(result)
        rtmp = re.findall('.*(?:file|streamer|hestia):\s*["\']([^\'"]+).*',result)[0]
        rtmp=rtmp.replace('rtmpe://l.mybeststream.xyz/r/','')
        url='rtmpe://l.mybeststream.xyz/r/'+ rtmp + ' swfUrl=http://mybeststream.xyz/jwplayer.flash.swf swfsize=61916 swfhash=e54728508e787f43cd472ef9ba2e514e2eca3f0679b3782206a3808b8d89b164 token=c.r.e.a.t.e.S.t. flashver=WIN\\2020,0,0,228 live=1 timeout=15 swfVfy=1 pageUrl=' + page
        return url
    except:
       return

