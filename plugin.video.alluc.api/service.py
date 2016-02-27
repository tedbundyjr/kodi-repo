import sys
import os
import time
import urllib
import math
import xbmc
from dudehere.routines import *
from datetime import datetime, date
test = xbmc.__version__.split('.')
is_depricated = True if int(test[1]) < 19  else False
def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

class AllucService():
	def __init__(self, *args, **kwargs):
		self.initiated = datetime.now()
		self.delay = 30
		self.timers = {}

	def log(self, message):
		xbmc.log("%s Service: %s" %(ADDON_NAME, message))

	def get_setting(self, setting):
		return ADDON.get_setting(setting)

	def get_bool_setting(self, setting):
		return  str2bool(ADDON.get_setting(setting))

	def set_setting(self, setting, value):
		return ADDON.set_setting(setting, value)

	def is_enabled(self):
		return self.get_bool_setting('auto_update')

	def set_last_run(self, event, runtime):
		self.set_setting('last-run_'+event,runtime)

	def timestamp(self, d):
		return time.mktime(d.timetuple())
	
	def convert_setting_to_hours(self, t):
		h = 0
		timers = [8, 12, 24]
		h=timers[int(t)]
		return h
	
	def get_next_run(self, f, delay=0):
		seconds =  f * 3600
		delay = delay * 60;
		today = date.today()
		zero = self.timestamp(today)
		now = self.timestamp(datetime.now())
		delta = (now - zero) / (seconds)
		offset = math.ceil(delta)
		next =  offset * seconds + (zero + delay)
		next = datetime.fromtimestamp(next)
		return next
		
	def get_last_run(self, event):
		runtime=self.get_setting('last-run_'+event)
		if runtime:
			try:
				lastrun = datetime.strptime(runtime, '%Y-%m-%d %H:%M:%S.%f')
			except TypeError:
				lastrun = datetime.fromtimestamp(time.mktime(time.strptime(runtime, '%Y-%m-%d %H:%M:%S.%f')))
			return lastrun
		else:
			return self.initiated
	
	def clear_timers(self):
		self.log("Clearing timers...")
		self.set_last_run('tvshows', '')
		self.set_last_run('movies', '')
	
	def load_settings(self):
		self.log("Loading service settings...")
		self.enabled = self.get_bool_setting('auto_update')
		self.update_timer = self.convert_setting_to_hours(self.get_bool_setting('update_timer'))
		self.update_tvshows = self.get_bool_setting('update_tvshows')
		self.update_movies = self.get_bool_setting('update_movies')
	
	def _run_kodi_cmd(self, params):
		cmd = 'RunPlugin(plugin://%s/?%s)' % (ADDON_ID, params)
		xbmc.executebuiltin(cmd)


	def setup_timers(self):
		self.log("Initiating timers...")
		if not self.enabled:
			return
		if self.update_tvshows:
			nextrun = self.get_next_run(self.update_timer)
			self.log("Next tvshow update scheduled to run at %s" % nextrun)
			self.timers['tvshows'] = {}
			self.timers['tvshows']['lastrun'] = self.get_last_run('tvshows')
			self.timers['tvshows']['interval'] = self.update_timer
			self.timers['tvshows']['nextrun'] = nextrun
			self.timers['tvshows']['command'] = 'RunPlugin(plugin://' + ADDON_ID + '/?mode=autoupdate_tv)'	
		else:
			self.timers['tvshows'] = None
	
		if self.update_movies:
			nextrun = self.get_next_run(self.update_timer, delay=5)
			self.log("Next movie update scheduled to run at %s" % nextrun)
			self.timers['movies'] = {}
			self.timers['movies']['lastrun'] = self.get_last_run('movies')
			self.timers['movies']['interval'] = self.update_timer
			self.timers['movies']['nextrun'] = nextrun
			self.timers['movies']['command'] = 'RunPlugin(plugin://' + ADDON_ID + '/?mode=autoupdate_movie)'
		else:
			self.timers['movies'] = None
			
			
	def evaluate_timers(self):
		now = self.timestamp(datetime.now())
		if self.update_tvshows:
			if now > self.timestamp(self.timers['tvshows']['nextrun']):
				self.execute('tvshows')
		if self.update_movies:
			if now > self.timestamp(self.timers['movies']['nextrun']):
				self.execute('movies')

	def execute(self, event):
		self.log("Executing: %s" % event)
		self.log(str(datetime.now()))
		self.timers[event]['lastrun'] =  datetime.now()
		self.timers[event]['nextrun'] = self.get_next_run(self.timers[event]['interval'])
		self.set_last_run(event, str(self.timers[event]['lastrun']))
		xbmc.executebuiltin(self.timers[event]['command'])
		self.log("Next %s update scheduled to run at %s" % (event, self.timers[event]['nextrun']))
		self.log("Waiting for next event...")
	
	def start(self):
		self.log("Service starting...")
		self.load_settings()
		if self.enabled:
			self.clear_timers()
			self.setup_timers()
		self.run()
		
	def run(self):
		monitor = xbmc.Monitor()
		if is_depricated:
			while not xbmc.abortRequested:
				if self.enabled:
					self.evaluate_timers()
				if self.enabled != self.is_enabled():
					self.load_settings()
					self.setup_timers()
					self.log("Waiting for next event...")
				xbmc.sleep(10)
		else:
			while not monitor.abortRequested():
				if monitor.waitForAbort(10):
					break
				if self.enabled:
					self.evaluate_timers()
				if self.enabled != self.is_enabled():
					self.load_settings()
					self.setup_timers()
					self.log("Waiting for next event...")

		self.log("Service stopping...")

if __name__ == '__main__':
	AC = AllucService()
	AC.start()

