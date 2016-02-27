from BeautifulSoup import BeautifulSoup as bs
from webutils import *
import client
import re


def resolve(url):
    #try:
        print(url)
        resolved=resolve_it(url)
        if resolved==None:
            url=find_link(url)
            resolved=url
            url=resolve_it(url)
            if url!=None:
                resolved=url
        return resolved
    #except:
       #return url



resolver_dict={ 'dailymotion.com': 'dailymotion',
				'spruto.tv' : 'spruto'
            
              }

def find_links(url):
    try: referer = urlparse.parse_qs(urlparse.urlparse(url).query)['referer'][0]
    except: referer = url
    html=client.request(url,referer=referer)
    html=urllib.unquote(html)

    ref=url
    fs=list(globals().copy())
    urls = []
    for f in fs:
        if 'finder' in f:
            resolved = eval (f+"(html,ref)")
            if resolved:
                print('Resolved with %s: %s'%(f,resolved))
                urls.append(resolved)
    return urls

#dailymotion
def finder1(html,url):
	try:
		url = re.findall('(https?://(?:www.)?dailymotion.com/[^"\']+)',html)[0]
		return ('Dailymotion.com',url)
	except:
		return
#spruto.tv
def finder2(html,url):
	try:
		url = re.findall('(https?://(?:www.)?spruto.tv/[^"\']+)',html)[0]
		return ('Spruto.tv',url)
	except:
		return

#youtube
def finder3(html,url):
	try:
		url = re.findall('(https?://(?:www.)?youtube.com/[^"\']+)',html)[0]
		return ('Youtube.com',url)
	except:
		return