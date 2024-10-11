import json
import sys
import typing
from packages.types.settings import Settings
from packages.cli.misc import clear
import colorama

class Menu:
	def __init__(self, name:str, settings:Settings) -> None:
		self.name: str = name
		self.entries:list[Entry] = []
		self.settings:Settings = settings
		# self.highlighted:int = 0

	def update(self, newName:str|None) -> None:
		if not newName: return
		self.name = newName
		self.loadEntries()

	def loadEntries(self) -> None:
		elements = json.load(open(f"./data/directory/{self.name}.json"))
		self.entries.clear()
		for e in elements:
			self.entries.append(globals()[e["build_function"]](self, e))

	def select(self, acceptNone:bool=False) -> typing.Any:
		filtered = list(filter(lambda E: not isinstance(E, DivEntry), self.entries))
		while True:
			self.flush()
			inp:str = input(self.settings.lang.translate("input_menu_select").format(menu=self.name))
			if inp.isnumeric() and int(inp) < len(filtered): break
			elif acceptNone: return
		print()
		return filtered[int(inp)]

	# def highlightUp(self) -> None:
	# 	if self.highlighted > 0:
	# 		self.highlighted -= 1
			
	# def highlightDown(self) -> None:
	# 	if self.highlighted < len(self.entries)-1:
	# 		self.highlighted += 1

	# def highlight(self, key:(Key|KeyCode|None)) -> None|bool:
	# 	if key == Key.enter: return False
	# 	if key in [Key.up, Key.left]:
	# 		self.highlightUp()
	# 	if key in [Key.down, Key.right]:
	# 		self.highlightDown()
	# 	self.flush()

	# def select(self) -> typing.Any:
	# 	filtered = list(filter(lambda E: not isinstance(E, DivEntry), self.entries))
	# 	self.flush()
	# 	with Listener(on_release=self.highlight) as listener: # type: ignore
	# 		listener.join()
	# 	del listener
	# 	print()
	# 	return filtered[self.highlighted]

	def flush(self) -> None:
		clear()
		pad:int = len(str(len(self.entries)))
		e:int = 0
		resetC:str = colorama.Style.RESET_ALL
		for i in range(len(self.entries)):
			backC:str = ""
			# if i == self.highlighted:
			# 	backC = colorama.Back.LIGHTYELLOW_EX
			c:str = str(self.entries[i].style.fore if self.entries[i].style.fore else "")
			if len(backC) > 0:
				c+=backC
			else:
				c+=str(self.entries[i].style.back if self.entries[i].style.back else "")
			desc:str = self.settings.lang.translate(self.entries[i].description)
			if isinstance(self.entries[i], DivEntry):
				print(c + desc.center(20) + resetC)
				continue
			print(c + f"[{str(e).rjust(pad)}] " + desc + resetC)
			e+=1

class Style:
	def __init__(self, data:dict[str, dict[str, str|None]]) -> None:
		self.fore:str|None = getattr(colorama.Fore, data["style"]["fore"].upper()) if data["style"]["fore"] else None
		self.back:str|None = getattr(colorama.Back, data["style"]["back"].upper()) if data["style"]["back"] else None
		self.dim:str|None = getattr(colorama.Style, data["style"]["style"].upper()) if data["style"]["style"] else None

class Entry:
	def __init__(self, desc:str, style:Style) -> None:
		self.description:str = desc
		self.style:Style = style

class DivEntry(Entry):
	def __init__(self, desc:str, style:Style) -> None:
		super().__init__(desc, style)

class MenuPointer(Entry):
	def __init__(self, desc:str, style:Style, next_menu:str|None, prev_menu:str|None, parent:Menu) -> None:
		super().__init__(desc, style)
		self.next_menu:str|None = next_menu
		self.prev_menu:str|None = prev_menu
		self.parent:Menu = parent

class ExecutableEntry(Entry):
	def __init__(self, desc:str, style:Style, function:typing.Callable[..., typing.Any]|None, params:dict[str, typing.Any], parent:Menu) -> None:
		super().__init__(desc, style)
		self.function:typing.Callable[..., typing.Any]|None = function
		self.params:dict[str, typing.Any] = params
		self.parent:Menu = parent

	def run(self) -> typing.Any:
		if not callable(self.function): return None
		if self.params.get("settings") != None:
			self.params["settings"] = self.parent.settings
			return self.function(**self.params)
		try:
			return self.function(**self.params)
		except Exception as e:
			raise e

class ObjectExecutableEntry(Entry):
	def __init__(self, desc:str, style:Style, function:typing.Callable[..., typing.Any]|None, params:dict[str, typing.Any], parent:Menu) -> None:
		super().__init__(desc, style)
		self.function:typing.Callable[..., typing.Any]|None = function
		self.params:dict[str, typing.Any] = params

	def run(self) -> typing.Any:
		if not callable(self.function): return None
		return self.function(**self.params)

def menuPointerFromJson(obj:Menu, data:dict[str, typing.Any]) -> MenuPointer:
	return MenuPointer(
		data["description"],
		Style(data),
		data["next_menu"],
		data["prev_menu"],
		parent=obj
	)

def executableFromJson(obj:Menu, data:dict[str, typing.Any]) -> ExecutableEntry:
	return ExecutableEntry(
		data["description"],
		Style(data),
		getattr(
			__import__(data["module"], fromlist=[None]), # type: ignore
			data["function"]
		) if data["function"] else None,
		data["params"],
		parent=obj
	)

def objectExecutableFromJson(obj:Menu, data:dict[str, typing.Any]) -> ObjectExecutableEntry:
	return ObjectExecutableEntry(
		data["description"],
		Style(data),
		getattr(
			getattr(obj, data["attribute"]),
			data["function"]
		) if data["function"] else None,
		data["params"],
		parent=obj
	)

def divFromJson(obj:Menu, data:dict[str, typing.Any]) -> DivEntry:
	return DivEntry(
		data["description"],
		Style(data)
	)

def exit(settings:Settings) -> None:
	inp:str = input(settings.lang.translate("exit_input"))
	if inp.lower() != "y": return
	sys.exit()