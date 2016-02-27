import xbmc
import xbmcaddon
from dudehere.routines import *
from dudehere.routines.vfs import VFSClass
try:
	KODI_LANGUAGE = xbmc.getLanguage().lower()
except:
	KODI_LANGUAGE = 'english'
LANGUAGE_PATH = VFSClass().join(ROOT_PATH, 'resources/language/' + KODI_LANGUAGE)

def i18n(id):
	return xbmcaddon.Addon().getLocalizedString(id).encode('utf-8', 'ignore')