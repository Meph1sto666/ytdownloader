import os
from packages.types.settings import Settings

def getAllFilesRecursively(path:str) -> list[str]:
    if not os.path.isdir(path): return [path]
    f_list:list[str] = []
    for p in os.listdir(path):
        f_list.extend([sp for sp in getAllFilesRecursively(path + os.sep + p)])
    return f_list

def clear(header:bool=True) -> None:
	os.system('cls' if os.name == 'nt' else 'clear')
	if header:
		print(createHeader())

def beautifyFSize(sizeByte:int, roundDecimal:int=2) -> str:
	if sizeByte == 0: return "0B"
	nums:list[str] = ["B", "KB", "MB", "GB", "TB"]
	for i in range(len(nums)-1, -1, -1):
		if 1024**i > sizeByte: continue
		return f"{round(sizeByte/(1024**i), roundDecimal)}{nums[i]}"
	return "0B"

def createHeader() -> str:
	cacheFiles:list[str] = getAllFilesRecursively("./data/cache")
	os.makedirs("./data/cache", exist_ok=True)
	cacheSize:int = sum([os.path.getsize(f) for f in cacheFiles])
	downloadFiles:list[str] = getAllFilesRecursively("./downloads")
	os.makedirs("./downloads", exist_ok=True)
	downloadSize:int = sum([os.path.getsize(f) for f in downloadFiles])

	header:str = f"CACHE: [{beautifyFSize(cacheSize)}] DOWNLOADS: [{beautifyFSize(downloadSize)}]"
	return header

def clear_cache(settings:Settings, folder:str) -> None:
	inp: str = input(settings.lang.translate("input_clear_cache"))
	if inp.lower() != "y": return
	for f in getAllFilesRecursively(folder):
		os.remove(f)