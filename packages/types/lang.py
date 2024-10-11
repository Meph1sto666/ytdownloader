import json
import os

class Lang:
	"""
		language class for translations
	"""
	def __init__(self, lang:str="en_us") -> None:
		self.lang:str = lang
	
	def readTable(self) -> dict[str, str]:
		return json.load(open(f"./data/lang/{self.lang}.json"))
	
	def translate(self, key:str) -> str:
		return self.readTable().get(key, f"<{self.lang}.{key}>")

def getAvailableLangs() -> list[str]:
	"""
		returns a list of all available language files in the language folder
	"""
	return os.listdir("./data/lang/")