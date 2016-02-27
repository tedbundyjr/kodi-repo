import os
import sys
import urllib2
import xbmc
import xbmcgui
import xbmcaddon
import hashlib
import base64
from urllib2 import URLError, HTTPError
WINDOW_PREFIX = 'transmogrifier'
try: 
	import simplejson as json
except ImportError: 
	import json

def set_property(k, v):
	k = "%s.%s" % (WINDOW_PREFIX, k)
	xbmcgui.Window(10000).setProperty(k, str(v))
	
def get_property(k):
	k = "%s.%s" % (WINDOW_PREFIX, k)
	p = xbmcgui.Window(10000).getProperty(k)
	if p == 'false': return False
	if p == 'true': return True
	return p

def clear_property(k):
	k = "%s.%s" % (WINDOW_PREFIX, k)
	xbmcgui.Window(10000).clearProperty(k)
	
class TransmogrifierAPI:
	def __init__(self):
		self.use_remote_host = xbmcaddon.Addon(id='service.transmogrifier').getSetting('connect_remote') == 'true'
		if self.use_remote_host:
			self.host = xbmcaddon.Addon(id='service.transmogrifier').getSetting('remote_host')
			self.pin = xbmcaddon.Addon(id='service.transmogrifier').getSetting('remote_auth_pin')
			self.token = xbmcaddon.Addon(id='service.transmogrifier').getSetting('remote_auth_token')
			self.port = xbmcaddon.Addon(id='service.transmogrifier').getSetting('remote_control_port')
		else:
			self.host = 'localhost'
			self.pin = xbmcaddon.Addon(id='service.transmogrifier').getSetting('auth_pin')
			self.token = xbmcaddon.Addon(id='service.transmogrifier').getSetting('auth_token')
			self.port = xbmcaddon.Addon(id='service.transmogrifier').getSetting('control_port')
		self.save_directory = xbmcaddon.Addon(id='service.transmogrifier').getSetting('save_directory')
		self._authorize()
		
	def get_progress(self):
		return self._call('progress')
	
	def notify(self, message):
		image = os.path.join(xbmc.translatePath( xbmcaddon.Addon(id='service.transmogrifier').getAddonInfo('path') ), 'icon.png')
		cmd = "XBMC.Notification(TransmogrifierAPI, %s, 1500, %s)" % (message, image)
		xbmc.executebuiltin(cmd)
	
	def _authorize(self):
		if self.token == '':
			response = self._call("authorize")
			self.token = response['token']
			if xbmcaddon.Addon(id='service.transmogrifier').getSetting('connect_remote') == 'true':
				xbmcaddon.Addon(id='service.transmogrifier').setSetting('remote_auth_token', self.token)
			else:
				xbmcaddon.Addon(id='service.transmogrifier').setSetting('auth_token', self.token)
		else:
			response = self._call("validate_token")
			if 'success' not in response.keys():
				if xbmcaddon.Addon(id='service.transmogrifier').getSetting('connect_remote') == 'true':
					xbmcaddon.Addon(id='service.transmogrifier').setSetting('remote_auth_token', '')
				else:
					xbmcaddon.Addon(id='service.transmogrifier').setSetting('auth_token', '')
	
	def get_cached_file(self, title, season=None, episode=None, year=None):
		from dudehere.routines.vfs import VFSClass
		vfs = VFSClass()
		if season is not None:
			for extension in ['avi', 'mkv', 'mov', 'mp4', 'flv']:
				path = vfs.join(self.save_directory, "TV Shows/%s %sx%s.%s" % (title, season, episode, extension))
				if vfs.exists(path):
					return path
			return False
		else:
			for extension in ['avi', 'mkv', 'mov', 'mp4', 'flv']:
				path = vfs.join(self.save_directory,"Movies/%s (%s).%s" % (title, year, extension))
				if vfs.exists(path):
					return path
			return False
	
	def get_streaming_url(self, url, host=None):
		if not url.lower().startswith(("http://", "https://")): return url
		
		try:
			response = self._call('status')
			if response['status'] != 200: 
				print 'TransmogrifierAPI Error: Proxy Host down, restart service?'
				return url
		except:
			print 'TransmogrifierAPI Error: Proxy Host down, restart service?'
			return url
		if host is not None:
			response = self._call('blacklist', {"host": host})
			if response['status'] == 406:
				print 'TransmogrifierAPI Notice: Host [ %s ] is blacklist' % host
				return url

		file_id = hashlib.md5(url).hexdigest()
		set_property('streaming', "true")
		set_property('file_id', file_id)
		clear_property('abort_id')
		hash_url = base64.b64encode(url)
		stream_url = "http://%s:%s/stream/%s/%s" % (self.host, self.port, hash_url, file_id)
		return stream_url
	
	def start_buffering(self, url):
		url = url + '?start_buffering=true'
		request = urllib2.Request(url)
		f = urllib2.urlopen(request)
		f.read()
		f.close()
	
	def clean_queue(self):
		from dudehere.routines.plugin import Plugin
		c = Plugin().confirm("Clean Queue", "Remove complete and failed?")
		if c: self._call("clear_queue")
	
	def enqueue(self, videos):
		if type(videos) is dict: videos = [videos]
		data = {"videos": videos}
		result = self._call('enqueue', data)
		try:
			if result['status'] == 200:
				self.notify('Successful Enqueue')
			else:
				self.notify('Enqueue Failed, review log for details')
		except:
			self.notify('Enqueue Failed, review log for details')
		return result
	
	def abort(self, file_id):
		return self._call('abort', {"file_id": file_id})
	
	def restart(self, ids):
		if type(ids) is int: ids = [ids]
		data = {"videos": []}
		for id in ids:
			data['videos'].append({"id": id})
		return self._call('restart', data)
	
	def delete(self, ids):
		if type(ids) is int: ids = [ids]
		data = {"videos": []}
		for id in ids:
			data['videos'].append({"id": id})
		return self._call('delete', data)
	
	
	
	def change_priority(self, id, priority):
		data = {"videos": [{"id": id, "priority": priority}]}
		return self._call('change_priority', data)
		
	def get_videos(self, media):
		from dudehere.routines.vfs import VFSClass
		vfs = VFSClass()
		if media == 'tv':
			path = vfs.join(self.save_directory, "TV Shows")
		else:
			path = vfs.join(self.save_directory, "Movies")
		videos = vfs.ls(path, pattern="(avi|mp4|mkv|mov|flv)$")[1]
		return path, videos
	
	def get_queue(self):
		return self._call('queue')
	
	def get_poll(self):
		return self._call('poll')
	
	def get_progress(self):
		return self._call('progress')
	
	def _build_url(self):
		url = "http://%s:%s/api.json" % (self.host, self.port)
		return url
	
	def _build_request(self, method):
		if method=='authorize':
			request = {"method": method, "pin": self.pin}
		else:
			request = {"method": method, "token": self.token}
		return request
	
	def _call(self, method, data=None):
		
		url = self._build_url()
		request = self._build_request(method)
		if data:
			for key in data.keys():
				request[key] = data[key]
		json_data = json.dumps(request)
		headers = {'Content-Type': 'application/json'}
		try:
			request = urllib2.Request(url, data=json_data, headers=headers)
			f = urllib2.urlopen(request)
			response = f.read()
			return json.loads(response)
		except HTTPError as e:
			print 'TransmogrifierAPI Error: %s' % e
