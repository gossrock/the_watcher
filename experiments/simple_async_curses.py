import asyncio
import curses
import curses.panel
from abc import ABC
import time

from task_looper import TaskLoopBase, keyboard_interuptable_loop_coroutine

from typing import Optional, Union, cast


#Base UI
class BaseUI(ABC, TaskLoopBase):
	def __init__(self, rate:float=1) -> None:
		super(BaseUI, self).__init__()
		self.rate:float = rate
		self.screens:List['BaseScreen'] = []
		self.active_screen:int = -1
		
	def __enter__(self) -> 'BaseUI':
		self.main_window = curses.initscr()
		self.main_window.nodelay(True)
		self.main_window.keypad(True)
		curses.noecho()
		curses.start_color()
		super(BaseUI, self).__enter__()
		return self
	
	def setup(self) -> None: ... #this will be called (By TaskLooperBase) at the end of all __enter__tasks
	
	def __exit__(self, *args) -> None:
		super(BaseUI, self).__exit__(*args)
		curses.nocbreak()
		curses.endwin()	
	
	def cleanup(self) -> None: ... #this will be called (by TaskLooperBase) at the begining of the __exit__ cycle
	
	
	@keyboard_interuptable_loop_coroutine
	async def screen_updater(self) -> None:
		'''
			a Job that is used to refresh the screen at the specified frame rate
		'''
		asyncio.sleep(self.rate)
		curses.doupdate()
		
	@keyboard_interuptable_loop_coroutine
	async def keyboard_listener(self) -> None:
		key = await self.get_key()
		if key is not None:
			
			self.main_window.noutrefresh()
			self.key_stroke_handler(key)
	
	async def get_key(self) -> Union[str,int,None]:
		await asyncio.sleep(0.1) 
		
		ch:Union[str, bytes, int, None] = None
		try:
			ch = self.main_window.get_wch()
		except curses.error as e:
			return None
		if type(ch) == bytes:
			ch = str(ch)
		return cast(Union[str,int,None],ch)
		
	def key_stroke_handler(self, key:Union[str, int]) -> None:
		if key == curses.KEY_PPAGE:
			self.next_screen()
			
		elif key == curses.KEY_NPAGE:
			self.prev_screen()
		
	
	#
	def add_screen(self, screen:'BaseScreen') -> None:
		self.screens.append(screen)
		if self.active_screen == -1:
			self.active_screen = 0
		
	def next_screen(self):
		screen_to_activate = (self.active_screen + 1) % len(self.screens)
		self.screens[screen_to_activate].raise_to_top()
		
	def prev_screen(self):
		screen_to_activate = (self.active_screen - 1) % len(self.screens)
		self.screens[screen_to_activate].raise_to_top()
		
	def raise_screen(self, screen):
		screen.panel.top()
		self.active_screen = self.screens.index(screen)



#
class BaseScreen(ABC):
	def __init__(self, parent:BaseUI) -> None:
		self.parent:BaseUI = parent
		self.parent.add_screen(self)
		maxy, maxx = self.parent.main_window.getmaxyx()
		self.window = parent.main_window.derwin(maxy, maxx, 0, 0)
		self.window.nodelay(True)
		self.window.keypad(True)
		
		self.panel = curses.panel.new_panel(self.window)
		
	def raise_to_top(self) -> None:
		self.parent.raise_screen(self)
		
	
class SimplestScreen(BaseScreen):
	pass
	
# 
class TextArea:
	pass





# Tests
class SimplestUI(BaseUI):
	def key_stroke_handler(self, key:Union[str,int]) -> None:
		self.main_window.addstr(str(key))
		self.main_window.noutrefresh()

class ScreenUI(BaseUI):
	def setup(self) -> None:
		self.num_screen = SimplestScreen(self)
		self.add_screen(self.num_screen)
		
		self.letter_screen = SimplestScreen(self)
		self.add_screen(self.letter_screen)
		
		self.num_screen.window.addstr('1234567')
		self.num_screen.window.noutrefresh()
		curses.panel.update_panels()
		curses.doupdate()
		time.sleep(1)
		
		self.letter_screen.window.addstr('ABCDEFG')
		self.letter_screen.window.noutrefresh()
		curses.panel.update_panels()
		curses.doupdate()
		time.sleep(1)
		
		while True:
			print('1')
			self.letter_screen.panel.hide()
			self.num_screen.panel.show()
			curses.panel.update_panels()
			
			self.num_screen.window.addstr('B')
			self.num_screen.window.noutrefresh()
			
			curses.doupdate()
			time.sleep(1)
			
			print('2')
			self.num_screen.panel.hide()
			self.letter_screen.panel.show()
			curses.panel.update_panels()
			
			self.letter_screen.window.addstr('A')
			self.letter_screen.window.noutrefresh()
			curses.panel.update_panels()
			curses.doupdate()
			time.sleep(1)
		
		
	
	def key_stroke_handler(self, key:Union[str,int]) -> None:
		super(BaseUI, self).key_stroke_handler(key)
		self.num_screen.window.addstr(str(key))
		self.num_screen.window.noutrefresh()	



def test():
	print('starting tests')
	
	print('BaseUI test 1')
	#with SimplestUI() as ui:
	#	ui.add_task(ui.keyboard_listener())
	#	ui.add_task(ui.screen_updater())
	#	ui.run_until_complete()
	
	print('BaseScreen test 1')
	with ScreenUI() as ui:
		ui.add_task(ui.keyboard_listener())
		ui.add_task(ui.screen_updater())
		ui.run_until_complete()
	
	print('ending tests')
	

if __name__ == '__main__':
	test()

