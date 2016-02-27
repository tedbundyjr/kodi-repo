import xbmc
import xbmcgui
import time
import math
from datetime import datetime, date
from lib.dudehere.routines import *
from lib.dudehere.routines.vfs import VFSClass
test = xbmc.__version__.split('.')
is_depricated = True if int(test[1]) < 19  else False

WINDOW_PREFIX = 'GenericPlaybackService'
def str2bool(v):
	return v.lower() in ("yes", "true", "t", "1")

class PlaybackService(xbmc.Player):
	def __init__(self, *args, **kwargs):
		xbmc.Player.__init__(self, *args, **kwargs)
		self.win = xbmcgui.Window(10000)
		self.initiated = datetime.now()
		self.__tracking 			= False
		self.__current_time 		= 0
		self.__total_time			= 0
		self.__percent 				= 0
	
	def log(self, message):
		xbmc.log("%s Service: %s" % (ADDON_NAME, message))
	
	def startup_log(self):
		vfs = VFSClass()
		self.log('Version: %s' % VERSION)
		msg = 'Repository installed: %s' % (xbmc.getCondVisibility('System.HasAddon(repository.dudehere.plugins)') == 1)
		self.log(msg)
		msg = 'Transmogrifier installed: %s' % (xbmc.getCondVisibility('System.HasAddon(service.transmogrifier)') == 1)
		self.log(msg)
		
		mod = vfs.read_file(vfs.join(ROOT_PATH, 'resources/mod.txt'))
		xbmc.log(mod)
	
	def set_property(self, k, v):
		self.win.setProperty(WINDOW_PREFIX + '.' + k, v)
	
	def get_property(self, k):
		return self.win.getProperty(WINDOW_PREFIX + '.' + k)
		
	def onPlayBackStarted(self):
		self.__tracking = str2bool(self.get_property('playing'))
		if self.__tracking:
			self.log("Now I'm playing")
			self.__total_time = self.getTotalTime()
			self.set_property('playing', "true")
			self.set_property('percent', "")
			self.set_property('total_time', str(self.__total_time))

	def onPlayBackStopped(self):
		if self.__tracking:
			try:
				self.__percent = int(self.__current_time * 100 / self.__total_time )
			except:
				self.__percent = 0
			self.log("Now I'm stopped at %s%s" % (self.__percent, '%'))
			self.set_property('percent', str(self.__percent))
			self.set_property('current_time', str(self.__current_time))
			self.set_property('total_time', str(self.__total_time))
			self.set_property('playing', "false")
	def onPlayBackEnded(self):
		self.onPlayBackStopped()

	def start(self):
		if not str2bool(ADDON.get_setting('enable_playback_service')): return
		monitor = xbmc.Monitor()
		self.log("Starting...")
		self.startup_log()
		if is_depricated:
			while not xbmc.abortRequested:
				if self.isPlaying() and self.__tracking:
					self.__current_time = self.getTime()
					self.__total_time = self.getTotalTime()
				xbmc.sleep(1000)
		else:
			while not monitor.abortRequested():
				if monitor.waitForAbort(1):
					break
				if self.isPlaying() and self.__tracking:
					self.__current_time = self.getTime()
					self.__total_time = self.getTotalTime()

		self.log("Service stopping...") 

if __name__ == '__main__':
	server = PlaybackService()
	server.start()