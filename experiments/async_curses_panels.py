import asyncio
import curses
import time
#from collections import namedtuple

from typing import Callable, Set, List, NamedTuple
from asyncio import Task
from asyncio.events import AbstractEventLoop


DEFAULT_COLOR = 1

TESTING = False


#### ASYNC UTILS ####
async def keep_running_till_all_others_complete(loop:AbstractEventLoop) -> None:
	'''
		This function is used to keep a asyncio loop going until all other tasks
		have completed. It is meant to be called from the 'loop.run_until_complete' function
	'''
	tasks:Set[Task] = asyncio.Task.all_tasks(loop)
	done:bool = False
	while not done:
		await asyncio.sleep(0)
		done = True
		for task in tasks:
			if task.done() == False and task is not asyncio.Task.current_task(loop):
				done = False
				break

def keyboard_interuptable_loop_coroutine(f:Callable) -> Callable:
	'''
		This decorator is to be used with the TaskLoopBase class and helps
		with shutting down multiple tasks when there is a KeyboardInterrupt event.
	'''
	async def func_wrapper(*args, **kwargs):
		self = args[0] 
		while self.close == False:
			try:
				await asyncio.sleep(0)
				await f(*args, **kwargs)
			except KeyboardInterrupt as kbi:
				self.close = True
	return func_wrapper

class TaskLoopBase:
	'''
		This class is ment to be the Base for other classes that have a set
		of tasks that are, for the most part, infinate loops and are stopped by
		a KeyboardInterupt event. It also helps with simplifying the setup and
		running of these classes. TaskLoopBase is a context manager and should 
		be used with a 'with' block.
	'''
	def __init__(self) -> None:
		self.close:bool = False # the flag to let the looping tasks know when to shut down
		self.tasks:List[Task] = [] # a list of tasks to run in the asyncio loop. they should all be coroutines.
		
	def __enter__(self) -> 'TaskLoopBase':
		self.setup()
		return self
		
	def setup(self) -> None:
		'''
			called by the __enter__ method and is where sub-classes should
			do what is needed during the objects creation phase
		'''
		pass
		
	def __exit__(self, *args:List) -> None:
		self.cleanup()
		
	def cleanup(self) -> None:
		'''
			called by the __exit__ method and is where sub-classes should do
			what is needed during the objects shutdown phase.
		'''
		pass
	
	def add_task(self, task:Task) -> None:
		'''
			use this to add coroutines to the list of things that should run
			these should be created before calling the run_until_complete method
			below.
		'''
		self.tasks.append(task)
	
	def run_until_complete(self) -> None:
		loop:AbstractEventLoop = asyncio.get_event_loop()
		try:
			for task in self.tasks:
				asyncio.ensure_future(task)
			# This is for when a KeyboardInterupt happens inside a @keyboard_interuptable_loop_coroutine
			# this will more likely happen when there is more work to do in side the worker coroutines (some slight blocking)
			loop.run_until_complete(keep_running_till_all_others_complete(loop)) 
		except KeyboardInterrupt as kbi:
			if self.close is not True:
				self.close = True
				# This is for when a KeyboardInterupt happens inside a the "loop.run_forever/loop.run_until_complete" coroutine
				# This will more likely happen when there is very little work to be done (almost no blocking)
				loop.run_until_complete(keep_running_till_all_others_complete(loop))
	
	
	
	
	#Window
			# has:
			#	parent
			#	hight
			#	width
			#	y_start
			#	x_start
			#	curses_window
			#	
			# can:
			#	refresh
			#	resize
		
		#ContainerWindow
				# has:
				#	children list of other windows
				# can:
				#	add child
				#	remove child
				# will:
				#	refresh children when refreshed
				#	resize childern when resized
				
			#BaseUI
					# Parent is None
					# will:
					#	run a window refresher
					#	run a keyboard listener
			# 
	
	

#### CURSES UTILS ####
class WindowSize(NamedTuple):
	maxx:int
	maxy:int
	
class Window:
	def __init__(self, parent:'Window', height:int=-1, width:int=-1, 
					y_start:int=0, x_start:int=0, border:bool=False) -> None:
		self.parent:'Window' = parent
		self.c_border_window = None
		self.c_window = None
		self.c_panel = None
		
		
'''
	def content_size(self):
		maxy self.c_window.
		
	def total_size(self):
		
	def size(self):
'''

class BaseUI(TaskLoopBase):
	def __init__(self, rate:float=1) -> None:
		super(BaseUI, self).__init__()
		self.rate:float = rate
	
	def __enter__(self):
		self.main_window = curses.initscr()
		self.main_window.nodelay(True)
		self.main_window.keypad(True)
		curses.noecho()
		curses.start_color()
		return super(BaseUI, self).__enter__()
		self.setup()
		
	def setup(self):
		pass
	
	def __exit__(self, *args):
		self.cleanup()
		curses.nocbreak()
		curses.endwin()
		super(BaseUI, self).__exit__(*args)
	
	def cleanup(self):
		pass
		
	@property
	def maxyx(self):
		
		return self.main_window.getmaxyx()
		
	@keyboard_interuptable_loop_coroutine
	async def screen_updater(self):
		'''
			a Job that is used to refresh the screen at the specified frame rate
		'''
		asyncio.sleep(self.rate)
		curses.doupdate()
		
	@keyboard_interuptable_loop_coroutine
	async def keyboard_listener(self):
		key = await self.get_key()
		if key is not None:
			self.key_stroke_handler(key)


	async def get_key(self):
		await asyncio.sleep(0.1)
		ch = None
		try:
			ch = self.main_window.get_wch()
		except curses.error as e:
			return None
		return ch
		
	def key_stroke_handler(self, key):
		pass


	
#### TESTS ####	
class TestUI_1(TaskLoopBase):
	'''
		testing very little blocking
	'''
	@keyboard_interuptable_loop_coroutine
	async def test1(self, name):
		await asyncio.sleep(1)
		#time.sleep(1)
		print(f'running test 1 {name}')
		
class TestUI_2(TaskLoopBase):
	'''
		testing more blocking
	'''
	@keyboard_interuptable_loop_coroutine
	async def test1(self, name):
		#await asyncio.sleep(1)
		time.sleep(1)
		print(f'running test 1 {name}')	
		
def tests():
	print('starting')
	
	ui:BaseUI
	
	with TestUI_1() as ui:
		ui.add_task(ui.test1('A'))
		ui.add_task(ui.test1('B'))
		ui.run_until_complete()
	
	with TestUI_2() as ui:
		ui.add_task(ui.test1('C'))
		ui.add_task(ui.test1('D'))
		ui.run_until_complete()
		
	print('ending')

if __name__=='__main__':
	tests()
