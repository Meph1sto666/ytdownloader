import pickle
import typing
import colorama
from packages.types.lang import Lang, getAvailableLangs
# from pynput.keyboard import Key, Listener, KeyCode

class Settings:
	"""
		class for settings such as language or song look-up
	"""
	def __init__(self) -> None:
		self.lang:Lang = Lang()
		self.thumbnail_size:int = 1024
		self.frame_as_cover:bool = False
		self.search_song_if_vid:bool = True
		self.song_diffing_threshold:float = 0.85

		self.audio_codec:typing.Literal['m4a', 'mp3'] = "m4a"
		self.add_lyrics:bool = True

		self.audio_download_path:str = "./downloads/audio/"
		self.video_download_path:str = "./downloads/video/"

		self.audio_name_pattern:str = '{artist} - {title}'
		self.video_name_pattern:str = '{author} - {title}'

		self.illegal_characters_regex:str = r'[^_\-\w\d]'
		self.illegal_characters_regex_replace_string:str = '-'

		# self.highlighted:int = 0

	# def highlightUp(self) -> None:
	# 	if self.highlighted > 0:
	# 		self.highlighted -= 1
			
	# def highlightDown(self, amount:int) -> None:
	# 	if self.highlighted < amount-1:
	# 		self.highlighted += 1

	# def highlight(self, key:(Key|KeyCode|None), amount:int, flushFunc) -> None|bool:
	# 	if key == Key.enter: return False
	# 	if key in [Key.up, Key.left]:
	# 		self.highlightUp()
	# 	if key in [Key.down, Key.right]:
	# 		self.highlightDown(amount)
	# 	flushFunc()

	# def langFlush(self) -> None:
	# 	langs:list[str] = getAvailableLangs()
	# 	pad:int = len(str(len(langs)))
	# 	for l in range(len(langs)):
	# 		print((colorama.Back.WHITE if langs[l].removesuffix(".json") == self.getLangName() else colorama.Back.RESET) + f"[{str(l).rjust(pad)}] {langs[l].removesuffix('.json')}" + colorama.Back.RESET)

	# def setLang(self) -> None:
	# 	self.langFlush()
	# 	langs:list[str] = getAvailableLangs()
	# 	with Listener(on_release=self.highlight, kwargs={"amount":len(langs), "flushFunc":self.langFlush}) as listener: # type: ignore
	# 		listener.join()

	# 	# if inp.isnumeric() and int(inp) < len(langs):
	# 	self.lang.lang = langs[self.highlighted].removesuffix(".json")
	# 	self.highlighted = 0

	def setLang(self) -> None:
		langs:list[str] = getAvailableLangs()
		pad:int = len(str(len(langs)))
		for l in range(len(langs)):
			print((colorama.Back.WHITE if langs[l].removesuffix(".json") == self.getLangName() else colorama.Back.RESET) + f"[{str(l).rjust(pad)}] {langs[l].removesuffix('.json')}" + colorama.Back.RESET)
		inp:str = input(self.lang.translate("input_language_select"))
		if inp.isnumeric() and int(inp) < len(langs):
			self.lang.lang = langs[int(inp)].removesuffix(".json")

	def setAudioCodec(self, codecs:list[typing.Literal['m4a', 'mp3']]) -> None:
		pad:int = len(str(len(codecs)))
		for l in range(len(codecs)):
			print((colorama.Back.WHITE if codecs[l] == self.audio_codec else colorama.Back.RESET) + f"[{str(l).rjust(pad)}] {codecs[l]}" + colorama.Back.RESET)
		inp:str = input(self.lang.translate("input_audio_codec_select"))
		if inp.isnumeric() and int(inp) < len(codecs):
			self.audio_codec = codecs[int(inp)]

	def alternateBool(self, setting:str) -> None:
		set:bool = self.__getattribute__(setting)
		set = not set
		
	def getLangName(self) -> str:
		return self.lang.lang
	
	def save(self) -> None:
		pickle.dump(self, open('./data/settings.pkl', 'wb'))

def load() -> Settings:
	try:
		return pickle.load(open('./data/settings.pkl', 'rb'), encoding='utf-8')
	except:
		return Settings()
	