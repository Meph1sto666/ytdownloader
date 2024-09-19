import os
import typing
import requests
import ytmusicapi # type: ignore
import pytube # type: ignore
import difflib
import re
from packages.types.album import MetaAlbum
from packages.types.settings import Settings
from ffmpeg.ffmpeg import FFmpeg # type: ignore
from mutagen.id3 import APIC, ID3, SYLT, Encoding, USLT # type: ignore
from mutagen.mp3 import MP3;
from mutagen.mp4 import MP4, MP4Cover
from mutagen.easyid3 import EasyID3
import lrclib.api # type: ignore
import yt_dlp
lrclibapi = lrclib.api.LrcLibAPI("urmum")

class Song:
	"""
		song class for downloading from yt, converting and setting metadata if found
	"""
	def __init__(self, url:str, settings:Settings) -> None:
		self.__downloadpath:str = settings.audio_download_path
		self.__vidCache:str = './data/cache/mp4/'
		self.__coverCache:str = './data/cache/covers/'
		for p in [self.__downloadpath, self.__vidCache, self.__coverCache]:
			os.makedirs(p, exist_ok=True)
		
		self.ytvid = pytube.YouTube(url, self.__callback) # type: ignore
		self.ytmusicSong:dict[str, str|None] = list(ytmusicapi.YTMusic().get_watch_playlist(self.ytvid.video_id, limit=1).get("tracks"))[0] # type: ignore
		self.__update(settings)
		self.cover:str = self.getCover(settings.frame_as_cover, settings.thumbnail_size)
		self.codec:typing.Literal['m4a', 'mp3'] = settings.audio_codec

		self.title:str|None = self.ytmusicSong.get("title") # type: ignore
		self.artist:str = '& '.join([i['name'] for i in self.ytmusicSong.get('artists')]) # maybe switch back to ' & ' if iTunes makes slashes # type: ignore
		self.albumId:str|None = self.ytmusicSong.get('album', {}).get("id") if not self.ytmusicSong.get('album') == None else None # type: ignore
		self.explicit:bool = self.ytmusicSong.get('isExplicit') or self.ytvid.age_restricted or getExplicityRating(self.ytvid.initial_data) # type: ignore

		self.year:str = self.ytmusicSong.get('year') or str(self.ytvid.publish_date.year) # type: ignore
		self.albumMetadata:MetaAlbum|None = MetaAlbum(self.albumId) if self.albumId != None else None # type: ignore
		self.trackPosition:int|None = self.albumMetadata.getTrackPos(self.title, self.ytvid.video_id) if self.albumId != None else None # type: ignore
		if settings.add_lyrics:
			self.lyrics:dict[str, str|None]|None = self.searchLyrics()
		
		self.filename:str = re.sub(rf'{settings.illegal_characters_regex_replace_string}+', settings.illegal_characters_regex_replace_string, re.sub(settings.illegal_characters_regex, settings.illegal_characters_regex_replace_string, settings.audio_name_pattern.format(**self.metadataDict())))

	def metadataDict(self) -> dict[str, str|int|None]:
		return {
			"artist": self.artist,
			"title": self.title,
			"explicit": self.explicit,
			"year": self.year,
			"album": self.albumMetadata.album if self.albumMetadata != None else None,
			"album_artist": self.albumMetadata.albumArtist if self.albumMetadata != None else None,
			"album_year": self.albumMetadata.albumYear if self.albumMetadata != None else None,
			"album_track_count": self.albumMetadata.trackCount if self.albumMetadata != None else None,
			"album_id": self.albumId,
			"id": self.ytvid.video_id
		}

	def update(self, settings:Settings) -> None:
		self.__update(settings)
		self.title = self.ytmusicSong.get("title")
		self.artist = '; '.join([i['name'] for i in self.ytmusicSong.get('artists')]) # type: ignore maybe switch back to ' & ' if iTunes makes slashes
		self.albumId = self.ytmusicSong.get('album', {}).get("id") # type: ignore
		self.explicit = self.ytmusicSong.get('isExplicit') or self.ytvid.age_restricted # type: ignore
		self.year = self.ytmusicSong.get('year') or str(self.ytvid.publish_date.year) # type: ignore
		self.albumMetadata = MetaAlbum(self.albumId) if self.albumId != None else None # type: ignore
		self.cover = self.getCover(settings.frame_as_cover, settings.thumbnail_size)
		self.__downloadpath = settings.audio_download_path

	def __update(self, settings:Settings) -> None:
		if self.is_song() and settings.search_song_if_vid:
			searchRes:dict[str, typing.Any]|None = self.__search_song(settings)
			if searchRes!=None:
				self.ytmusicSong = searchRes
				self.ytvid:pytube.YouTube = self.ytvid.from_id(searchRes.get("videoId")) # type: ignore

	def __search_song(self, settings:Settings) -> dict[str, typing.Any]|None:
		print(self.ytvid.video_id, "__search_song")
		ogTitles:list[str] = [
			f"{getVideoChannelName(self.ytvid.initial_data)} - {getVideoTitle(self.ytvid.initial_data)}", # type: ignore
			f"{''.join([i['name'] for i in self.ytmusicSong.get('artists')])} - {self.ytmusicSong.get('title')}" # type: ignore
		]
		for originalTitle in ogTitles:
			found:list[dict[str, typing.Any]] = ytmusicapi.YTMusic().search(originalTitle, filter="songs")[:5] # type: ignore
			if len(found) < 1: return None
			for i in range(len(found)):
				vidTitInf:str = f"{''.join([i['name'] for i in found[i].get('artists')])} - {found[i].get('title')}" # type: ignore
				score:float = difflib.SequenceMatcher(None, originalTitle.lower(), vidTitInf.lower()).ratio()
				print(originalTitle, "///", vidTitInf, "///", score)
				if score >= settings.song_diffing_threshold and (found[i].get('videoType') == "MUSIC_VIDEO_TYPE_ATV"):
					return found[i]

	def getCover(self, useFrame:bool=False, size:int=-1) -> str:
		"""
			fetches the thumbnail of the song and downloads it to ./data/cache/covers
		"""
		file:str = f"{self.__coverCache}{self.ytvid.video_id}.jpg"
		if not useFrame:
			thumbnailUrl:str = (self.ytmusicSong.get("thumbnail") or self.ytmusicSong.get("thumbnails"))[0]["url"] # type: ignore
			thumbnailUrl:str = re.sub(r"\?\w+=[\w\-=&]+", "", thumbnailUrl) # type: ignore // remove all sizing arguments
			thumbnailUrl:str = re.sub(r"=w\d+-h\d+-l\d+-rj", "", thumbnailUrl) # type: ignore // remove all sizing arguments
			thumbnailUrl:str = re.sub(r"=w\d+-h\d+-s\d*-l\d+-rj", "", thumbnailUrl) # type: ignore // remove all sizing arguments
			
			if not ".jpg" in thumbnailUrl:
				depth:int = 1024
				if size > 512:
					thumbnailUrl += f"=w{size}-h{size}-l{depth}-rj"
			print(self.ytvid.video_id, thumbnailUrl)
			open(file, "wb").write(requests.get(thumbnailUrl).content) # type: ignore
		return file

	def is_song(self) -> bool:
		return self.ytmusicSong.get("videoType") != "MUSIC_VIDEO_TYPE_ATV"

	def __callback(self, a:typing.Any, b:bytes, i:int) -> None:
		print(a, i)

	def download(self) -> None:
		# print(self.ytvid.video_id, "download", self.ytvid.streams.get_audio_only().filesize) # type: ignore
		with yt_dlp.YoutubeDL(
			{
				'format': 'best',
				"outtmpl": f"{self.__vidCache}{self.ytvid.video_id}.mp4" #self.__vidCache + "/" + self.ytvid.video_id + ".mp4"
			}
		) as ydl:
			print(self.ytvid.watch_url)
			ydl.download(self.ytvid.watch_url)
			# self.ytvid.streams.get_audio_only().download(self.__vidCache, self.ytvid.video_id + ".mp4") # type: ignore

	def convert(self) -> None:
		# FFmpeg().input(self.__vidCache, self.ytvid.video_id+".mp4").output("./downloads/", self.ytvid.video_id+".mp3").execute()
		print(self.ytvid.video_id, "convert")
		if os.path.exists("./lib/ffmpeg.exe"):
			FFmpeg("./lib/ffmpeg.exe").option("y").input(self.__vidCache + self.ytvid.video_id + ".mp4").output(self.__downloadpath + self.filename + f".{self.codec}").execute() # type: ignore
		else:
			FFmpeg().option("y").input(self.__vidCache + self.ytvid.video_id + ".mp4").output(self.__downloadpath + self.filename + f".{self.codec}").execute() # type: ignore
	
	
	def addCover(self) -> None:
		# if not os.path.exists(mp3File): return;
		print(self.ytvid.video_id, "addCover")
		if self.codec == 'mp3':
			audio = MP3(self.__downloadpath + self.filename + ".mp3", ID3=ID3)
			audio.tags.add(APIC(mime='image/jpeg',type=3,desc=u'Cover',data=open(f"{self.__coverCache}{self.ytvid.video_id}.jpg",'rb').read())) # type: ignore
		else:
			audio = MP4(self.__downloadpath + self.filename + ".m4a")
			audio['covr'] = [MP4Cover(data=open(f"{self.__coverCache}{self.ytvid.video_id}.jpg",'rb').read())]
		audio.save() # type: ignore

	def searchLyrics(self) -> dict[str,str|None]|None:
		lyrics:dict[str, str|None] = {}
		res: lrclib.api.SearchResult = lrclibapi.search_lyrics(track_name=self.title, artist_name=self.artist, album_name=self.albumMetadata.album if self.albumMetadata else "")
		if len(res) < 1 or res[0].instrumental: return None
		lyrics['sylt'] = res[0].synced_lyrics
		lyrics['uslt'] = res[0].plain_lyrics
		return lyrics

	def addMetadata(self) -> None:
		# if not self.is_song(): return
		print(self.ytvid.video_id, "addMetadata")
		if self.codec == 'mp3':
			audio = EasyID3(self.__downloadpath + self.filename + ".mp3")
			audio["date"] = [self.year]
			audio["artist"] = [self.artist]
			audio["title"] = [self.title]
			if self.albumMetadata != None:
				audio["album"] = [self.albumMetadata.album]
				audio["albumartist"] = [self.albumMetadata.albumArtist]
				audio["tracknumber"] = [self.trackPosition, self.albumMetadata.trackCount]
		else:
			audio = MP4(self.__downloadpath + self.filename + ".m4a")
			audio["\xa9day"] = [self.year]
			audio["\xa9ART"] = [self.artist]
			audio["\xa9nam"] = [self.title]
			if self.albumMetadata != None:
				audio['\xa9alb'] = [self.albumMetadata.album]
				audio["aART"] = [self.albumMetadata.albumArtist]
				audio["trkn"] = [(self.trackPosition, self.albumMetadata.trackCount)]
		audio.save() # type: ignore
		if self.lyrics != None:
			self.addLyrics()
		if self.explicit:
			self.setItunesAdvisory()
		# "bpm": "bpm_id3tag",
		# "mood": "mood_id3tag",
		# "language": "language_id3tag",
		# "genre": "genre_id3tag"
	
	def addLyrics(self) -> None:
		if self.lyrics is None: return
		if self.codec == 'mp3' and self.lyrics['sylt'] is not None:
			tag = ID3(self.__downloadpath + self.filename + ".mp3")
			tag.setall("SYLT", [SYLT(encoding=Encoding.UTF8, lang="eng", format=2, type=1, text=sLyricsToSYLT(self.lyrics['sylt']))]) # type: ignore
			tag.setall("USLT", [USLT(encoding=Encoding.UTF8, lang="eng", format=2, type=1, text=self.lyrics['uslt'])]) # type: ignore
			tag.save() # type: ignore
		elif self.lyrics['uslt'] is not None:
			tag = MP4(self.__downloadpath + self.filename + ".m4a")
			tag['\xa9lyr'] = self.lyrics['uslt']
			tag.save() # type: ignore

	def setItunesAdvisory(self) -> None:
		if self.codec != 'm4a': return
		tag = MP4(self.__downloadpath + self.filename + ".m4a")
		tag['rtng'] = [1 if self.explicit else 0]
		tag.save() # type: ignore

	def fullDw(self) -> None:
		"""
			automatically convert metadata and cover
		"""
		self.download()
		self.convert()
		self.addMetadata()
		self.addCover()
def getVideoTitle(vidData:dict[str, typing.Any]) -> str:
	return vidData["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][0]["videoPrimaryInfoRenderer"]["title"]["runs"][0]["text"]
def getVideoChannelName(vidData:dict[str, typing.Any]) -> str:
	return vidData["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][1]["videoSecondaryInfoRenderer"]["owner"]["videoOwnerRenderer"]["title"]["runs"][0]["text"]
def getExplicityRating(vidData:dict[str, typing.Any]) -> bool:
	return re.search(r"explicit", str(vidData), flags=2) is not None

def sLyricsToSYLT(sync_lrc:str) -> list[tuple[str, int]]:
	sylt:list[tuple[str, int]] = []
	for sl in sync_lrc.split("\n"):
		ts:str = re.search(r"(?<=\[)\d+:\d+\.\d+(?=\])", sl).group() # type: ignore
		tss:list[str] = re.split(r"\.|:", ts)
		tssi = ((int(tss[0])*60+int(tss[1]))*1000)+(int(tss[2])*10)
		sylt.append((re.sub(r"\[\d+:\d+\.\d+\] ", "", sl), tssi))
	return sylt

def sLyricsToUSLT(lrc:str) -> str:
	return re.sub(r"\[\d+:\d+\.\d+\] ", "", lrc)