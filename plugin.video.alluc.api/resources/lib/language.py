from dudehere.routines import *
from dudehere.routines.vfs import VFSClass
vfs = VFSClass()

class LanguageClass():
	def __init__(self):
		lang_path = vfs.join(ROOT_PATH, 'resources/languages.txt')
		self._code_table = vfs.read_file(lang_path, json=True)
		self._lang_table = {}
		self._codes = ['all']
		self._languages = ['-- All --']
		for code in self._code_table.keys():
			self._codes.append(code)
			self._languages.append(self._code_table[code])
			self._lang_table[self._code_table[code]] = code
		self._languages.sort()
		
	def get_lang_by_code(self, code):
		try:
			return self._code_table[code]
		except:
			return False
	def get_code_by_lang(self, lang):
		try:
			return self._lang_table[lang]
		except:
			return False
	
	def get_languages(self):
		return self._languages
		
