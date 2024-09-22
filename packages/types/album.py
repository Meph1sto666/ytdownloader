import difflib
import ytmusicapi # type: ignore
import typing

class MetaAlbum:
	"""
		Class for metadata about albums for non recursive endless loop when having song metadata about album
	"""
	def __init__(self, albumId:str) -> None:
		albuminfo:dict[typing.Any, typing.Any] = ytmusicapi.YTMusic().get_album(albumId) # type: ignore
		self.album:str|None = albuminfo.get("title")
		self.trackCount:int|None = albuminfo.get("trackCount")
		self.albumArtist:str|None = ' & '.join([a.get("name") for a in (albuminfo.get("artists"))]) # back to ' & ' if it doesn't work properly # type: ignore
		self.albumYear:str|None = albuminfo.get("year")
		self.tracks:list[tuple[str, str]] = [(t.get("videoId"), t.get("title")) for t in albuminfo.get("tracks")] # type: ignore

	def getTrackPos(self, title:str, id:str|None) -> int | None:
		for t in range(len(self.tracks)):
			if id==self.tracks[t][0]: return t+1
			if difflib.SequenceMatcher(None, self.tracks[t][1].lower(), title.lower()).ratio() >= .95: return t+1
