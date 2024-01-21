import os # type: ignore
from packages.types.settings import Settings
from packages.types.song import Song
from packages.types.video import Video
from pytube import Playlist # type: ignore
import concurrent.futures

def download_audio(d:tuple[str, Settings]) -> None:
    Song(*d).fullDw()
def download_video(d:tuple[str, Settings]) -> None:
    Video(*d).download()

def download_video_playlist(settings:Settings) -> None:
    url:str = input(settings.lang.translate("input_playlist_url"))
    if url.isspace() or len(url) < 1: return
    with concurrent.futures.ThreadPoolExecutor() as exector:
        exector.map(download_video, [(u, settings) for u in Playlist(url).video_urls])
    os.system("reset")
    

def download_video_single(settings:Settings) -> None:
    url: str = input(settings.lang.translate("input_video_url"))
    if url.isspace() or len(url) < 1: return
    vid = Video(url, settings)
    vid.download()
    
def download_music_playlist(settings:Settings) -> None:
    url:str = input(settings.lang.translate("input_playlist_url"))
    if url.isspace() or len(url) < 1: return
    try:
        with concurrent.futures.ThreadPoolExecutor() as exector:
            exector.map(download_audio, [(u, settings) for u in Playlist(url).video_urls])
    except:
        raise
    os.system("reset")
    
def download_music_single(settings:Settings) -> None:
    url = input(settings.lang.translate("input_video_url"))
    if url.isspace() or len(url) < 1: return
    song = Song(url, settings)
    song.fullDw()