import os
import pytubefix as pytube
import tqdm # type: ignore
from packages.types.settings import Settings
import re

class Video:
	def __init__(self, url:str, settings:Settings) -> None:
		self.downloadpath:str = settings.video_download_path
		os.makedirs(self.downloadpath, exist_ok=True)
		self.ytvid = pytube.YouTube(url) # type: ignore
		self.filename:str = re.sub(rf'{settings.illegal_characters_regex_replace_string}+', settings.illegal_characters_regex_replace_string, re.sub(settings.illegal_characters_regex, settings.illegal_characters_regex_replace_string, settings.video_name_pattern.format(**self.metadataDict())))
		
	def metadataDict(self) -> dict[str, str|int|None]:
		return {
			'author': self.ytvid.author,
			'title': self.ytvid.title
		}

	def download(self) -> None:
		# print(self.ytvid.video_id, "download", self.ytvid.streams.get_highest_resolution().filesize) # type: ignore
		stream: pytube.Stream | None = self.ytvid.streams.get_highest_resolution()
		stream.download(self.downloadpath, self.filename + ".mp4") # type: ignore