import packages.types.settings as settings
from packages.cli.menu import ExecutableEntry, MenuPointer, Menu, ObjectExecutableEntry
import sys
import atexit

if __name__ == '__main__':
    s:settings.Settings = settings.load()
    sys.excepthook = s.save
    atexit.register(s.save)
    menu = Menu("main", s)
    menu.loadEntries()
    while True:
        selected = menu.select()
        if isinstance(selected, MenuPointer):
            menu.update(selected.next_menu)
        if isinstance(selected, ExecutableEntry|ObjectExecutableEntry):
            selected.run()