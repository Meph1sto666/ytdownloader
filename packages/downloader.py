import os
import typing # type: ignore
from packages.types.settings import Settings
from packages.types.song import Song
from packages.types.video import Video
from pytubefix import Playlist # type: ignore
import concurrent.futures
import tqdm

def download_audio(d:tuple[str, Settings]) -> None:
	Song(*d).fullDw()
def download_video(d:tuple[str, Settings]) -> None:
	Video(*d).download()

def download_video_playlist(settings:Settings) -> None:
	url:str = input(settings.lang.translate("input_playlist_url"))
	if url.isspace() or len(url) < 1: return
	with concurrent.futures.ThreadPoolExecutor() as exector:
		jobs: list[tuple[typing.Any, Settings]] = [(u, settings) for u in Playlist(url).video_urls]
		workers = exector.map(download_video, jobs)
		pbar = tqdm.tqdm(workers, total=len(jobs), ascii=".#", colour="#ff0000")
		list(pbar)
	os.system("reset")
	

def download_video_single(settings:Settings) -> None:
	url: str = input(settings.lang.translate("input_video_url"))
	if url.isspace() or len(url) < 1: return
	vid = Video(url, settings)
	vid.download()
	
def download_music_playlist(settings:Settings) -> None:
	url:str = input(settings.lang.translate("input_playlist_url"))
	if url.isspace() or len(url) < 1: return
	with concurrent.futures.ThreadPoolExecutor() as exector:
		jobs: list[tuple[typing.Any, Settings]] = [(u, settings) for u in Playlist(url).video_urls]
		workers = exector.map(download_audio, jobs)
		pbar = tqdm.tqdm(workers, total=len(jobs), ascii=".#", colour="#ff0000")
		list(pbar)
		# for _ in concurrent.futures.as_completed(workers)z:
		# 	pbar.update()

	os.system("reset")
	
def download_music_single(settings:Settings) -> None:
	url: str = input(settings.lang.translate("input_video_url"))
	if url.isspace() or len(url) < 1: return
	song = Song(url, settings)
	song.fullDw()
