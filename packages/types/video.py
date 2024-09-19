import os
import pytube # type: ignore
from packages.types.settings import Settings
import re
import yt_dlp

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
		with yt_dlp.YoutubeDL(
			{
				'format': 'best',
				"outtmpl": f"{self.downloadpath}{self.filename}.mp4" #self.__vidCache + "/" + self.ytvid.video_id + ".mp4"
			}
		) as ydl:
			ydl.download(self.ytvid.watch_url)

		# print(self.ytvid.video_id, "download", self.ytvid.streams.get_highest_resolution().filesize) # type: ignore
		# self.ytvid.streams.get_highest_resolution().download(self.downloadpath, self.filename + ".mp4") # type: ignore