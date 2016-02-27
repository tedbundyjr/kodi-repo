# -*- coding: utf-8 -*-
import re

def resolve(url,name):
	name = ''
	if 'sop://'in url:
		url='plugin://program.plexus/?mode=2&url=%s&name=%s'%(url,name.replace(' ','+'))
	elif 'acestream://' in url:
		url='plugin://program.plexus/?mode=1&url=%s&name=%s'%(url,name.replace(' ','+'))
	return url

