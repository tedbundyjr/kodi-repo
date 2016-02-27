#!/usr/bin/python
# -*- coding: utf-8 -*-
PYTHONIOENCODING="UTF-8"

'''*
	Copyright (C) 2015 DudeHere

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

*'''
import os
import sys
import xbmc
import xbmcaddon

from addon.common.addon import Addon

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	forward = dict((key, value) for key, value in enums.iteritems())
	reverse = dict((value, key) for key, value in enums.iteritems())
	enums['f_map'] = forward
	enums['r_map'] = reverse
	return type('Enum', (), enums)

def has_item(obj, key):
	if key in obj: return True
	for k, v in obj.items():
		if isinstance(v,dict):
			item = has_item(v, key)
			if item is not None:
				return True
	return False

class MyAddon(Addon):
	def log(self, msg, level=0):
		if level==1 or self.get_setting('log_level')=="1":
			if isinstance (msg,str):
				msg = msg.decode("utf-8")
			msg = u'%s' %  msg
			msg = msg.encode('utf-8')
			xbmc.log('%s v%s: %s' % (self.get_name(), self.get_version(), msg))
			
	def save_data(self, filename, data):
		import pickle
		profile_path = self.get_profile()
		try:
			os.makedirs(profile_path)
		except:
			pass
		save_path = os.path.join(profile_path, filename)
		try:
			pickle.dump(data, open(save_path, 'wb'))
			return True
		except pickle.PickleError:
			return False
		
	def load_data(self,filename):
		import pickle
		profile_path = self.get_profile()
		load_path = os.path.join(profile_path, filename)

		if not os.path.isfile(load_path):
			self.log_debug('%s does not exist' % load_path)
			return False
		try:
			data = pickle.load(open(load_path))
		except:
			return False
		return data

	def str2bool(self, v):
		if not v: return False
		return v.lower() in ("yes", "true", "t", "1")
	
	def get_bool_setting(self, k):
		return(self.str2bool(self.get_setting(k)))
	
	def raise_notify(self, title, message, timeout=3000):
		image = os.path.join(xbmc.translatePath( self.get_path() ), 'icon.png')
		cmd = "XBMC.Notification(%s, %s, %s, %s)" % (title, message, timeout, image)
		xbmc.executebuiltin(cmd)
	
	def raise_error(self, title, m1='', m2=''):
		import xbmcgui
		dialog = xbmcgui.Dialog()
		dialog.ok("%s ERROR!" % ADDON_NAME, title, str(m1), str(m2))

ARGV = sys.argv
try:
	int(ARGV[1])
except:
	ARGV.insert(1, -1)
try: 
	str(ARGV[2])
except:
	ARGV.insert(2, "?/fake")
PLATFORM = sys.platform
HANDLE_ID = int(ARGV[1])
ADDON_URL = ARGV[0]
PLUGIN_URL = ARGV[0] + ARGV[2]	
ADDON_ID = xbmcaddon.Addon().getAddonInfo('id')
ADDON_NAME =  xbmcaddon.Addon().getAddonInfo('name')
ADDON = MyAddon(ADDON_ID,ARGV)
ADDON_NAME = ADDON.get_name()
VERSION = ADDON.get_version()
ROOT_PATH = ADDON.get_path()
DATA_PATH = ADDON.get_profile()
ARTWORK = ROOT_PATH + '/resources/artwork/'
QUALITY = enum(LOCAL=9, HD1080=8, HD720=7, HD=6, HIGH=5, SD480=4, UNKNOWN=3, LOW=2, POOR=1)
LOG_LEVEL = enum(STANDARD=0, VERBOSE=1)

def utf8(string):
	try: 
		string = u'' + string
	except UnicodeEncodeError:
		string = u'' + string.encode('utf-8')
	except UnicodeDecodeError:
		string = u'' + string.decode('utf-8')
	return string