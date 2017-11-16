import asyncio
import curses
from abc import ABC
import time

from task_looper import TaskLoopBase, keyboard_interuptable_loop_coroutine

from typing import Optional, Union, cast


#Base UI
class BaseUI(ABC, TaskLoopBase):
	def __init__(self, rate:float=1) -> None:
		super(BaseUI, self).__init__()
		self.rate:float = rate
		
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
		
	#



#
class BaseScreen(ABC):
	pass
		
	
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
	



def test():
	print('starting tests')
	
	print('BaseUI test 1')
	with SimplestUI() as ui:
		ui.add_task(ui.keyboard_listener())
		ui.add_task(ui.screen_updater())
		ui.run_until_complete()

	
	print('ending tests')
	

if __name__ == '__main__':
	test()

