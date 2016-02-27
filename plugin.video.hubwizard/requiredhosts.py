import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,os,sys,time,shutil
import wizardmain as main
addon=main.addon; net=main.net; settings=main.settings; 
UA='Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0'
def FireDrive(url):
    if url.startswith('firedrive://'): url=url.replace('firedrive://','http://www.firedrive.com/file/')
    if ('http://m.firedrive.com/file/' not in url) and ('https://m.firedrive.com/file/' not in url) and ('http://www.firedrive.com/file/' not in url) and ('http://firedrive.com/file/' not in url) and ('https://www.firedrive.com/file/' not in url) and ('https://firedrive.com/file/' not in url): return url
    #else:
    try:
        html=net.http_GET(url).content
        if ">This file doesn't exist, or has been removed.<" in html: return "[error]  This file doesn't exist, or has been removed."
        elif ">File Does Not Exist | Firedrive<" in html: return "[error]  File Does Not Exist."
        elif "404: This file might have been moved, replaced or deleted.<" in html: return "[error]  404: This file might have been moved, replaced or deleted."
        #print html; 
        data={}; r=re.findall(r'<input\s+type="\D+"\s+name="(.+?)"\s+value="(.+?)"\s*/>',html);
        for name,value in r: data[name]=value
        #print data; 
        if len(data)==0: return '[error]  input data not found.'
        html=net.http_POST(url,data,headers={'User-Agent':UA,'Referer':url,'Host':'www.firedrive.com'}).content
        #print html
        r=re.search('<a\s+href="(.+?)"\s+target="_blank"\s+id=\'top_external_download\'\s+title=\'Download This File\'\s*>',html)
        if r: return urllib.unquote_plus(r.group(1))
        else: return url+'#[error]r'
    except: return url+'#[error]exception'
def ResolveOtherHosts(url):
    try:
        if url.startswith('host://'): 
        	url=url.replace('host://','http://')
        	try: 
        		import urlresolver
        		url=urlresolver.HostedMediaFile(url).resolve()
        		return url
        	except: return url+'#[error]urlresolver'
        else: return url
    except: return url+'#[error]exception'
def MrFile_dot_me(url):
    if url.startswith('mrfile://'): url=url.replace('mrfile://','http://mrfile.me/')
    if ('http://mrfile.me/' not in url) and ('http://www.mrfile.me/' not in url): return url
    try:
        html=net.http_GET(url).content
        #if '<h3 class="error_msg_title">Invalid or Deleted File.</h3>' in html: return "[error]  This file doesn't exist, or has been removed."
        data={}; r=re.findall(r'<input type="hidden"\s*name="(.+?)"\s*value="(.*?)"',html)
        for name,value in r: data[name]=value
        data['referer']=''; data['submit']='Click here to Continue'; data['method_free']=''; data['method_premium']=''; 
        html=main.nolines(net.http_POST(url,data).content).replace('<br><br><br>','<br>\r\a<br>\n<br>')
        r=re.search('<a href="(http\D*://.+?\.zip)">Download .+?\.zip</a>\s*</span',html)
        if r: return urllib.unquote_plus(r.group(1))
        else: return url+'#[error]r'
    except: return url+'#[error]exception'
def PromptFile(url):
    if url.startswith('promptfile://'): url=url.replace('promptfile://','http://www.promptfile.com/l/')
    if url.startswith('http://promptfile.com/'): url=url.replace('http://promptfile.com/','http://www.promptfile.com/')
    if ('http://www.promptfile.com/l/' not in url): return url
    try:
        html=main.nolines(net.http_GET(url,headers={'User-Agent':UA}).content).replace('/>','/\n\r>').replace('</div>','</div\n\r>')
        #if '<h3 class="error_msg_title">Invalid or Deleted File.</h3>' in html: return "[error]  This file doesn't exist, or has been removed."
        r=re.search('<a href="(http\D*://.+?)" class="green_btn download_btn">\s*Download File\s*</a',html)
        if not r:
            data={}; r=re.findall(r'<input type="hidden" name="(chash)" value="(.*?)"',html)
            for name,value in r: data[name]=value
            html=main.nolines(net.http_POST(url,data,headers={'User-Agent':UA,'Referer':url}).content).replace('</div>','</div\n\r>')
            r=re.search('<a href="(http\D*://.+?)" class="green_btn download_btn">Download File</a',html)
        if r: return urllib.unquote_plus(r.group(1))
        else: return url+'#[error]r'
    except: return url+'#[error]exception'
def CheckForHosts(url):
    #DefaultUrl=""+url
    #try:
        if 'https://' in url.lower(): url=url.replace('https://','http://')
        print {'incoming url':url}
        if url.startswith('host://'): url=ResolveOtherHosts(url)
        else:
            url=FireDrive(url)
            url=MrFile_dot_me(url)
            url=PromptFile(url)
        print {'returning url':url}
        return url
    #except: return DefaultUrl+'#[error]'
