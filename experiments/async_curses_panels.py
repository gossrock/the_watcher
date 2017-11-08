import asyncio
import curses
import time

DEFAULT_COLOR = 1


#### ASYNC UTILS ####
def keyboard_interuptable_loop_coroutine(f):
	async def func_wrapper(*args, **kwargs):
		self = args[0]
		name = args[1]
		print(f'{__name__}')
		while self.close == False:
			try:
				await asyncio.sleep(0)
				await f(*args, **kwargs)
			except KeyboardInterrupt as kbi:
				print(f'KeyboardInterup in keyboard_inteupable_loop_coroutine func_wrapper: {name}')
				self.close = True
				
		print(f'ending keyboard_inteupable_loop_coroutine func_wrapper: {name}: self.close: {self.close}')
	return func_wrapper

async def keep_running_till_all_others_complete(loop):
	tasks = asyncio.Task.all_tasks(loop)
	print('starting up loop_closer')
	not_done = True
	while not_done:
		not_done = False
		for task in tasks:
			if task.done() == False and task is not asyncio.Task.current_task(loop):
				not_done = True
				break
		await asyncio.sleep(0.1)
	
	print(f'closing down loop')

class TaskLoopBase:
	def __init__(self):
		self.close = False
		self.tasks = []
		
	def __enter__(self):
		return self
		
	def __exit__(self, *args):
		self.cleanup()
		
	def cleanup(self):
		pass
		
	
	
	def add_task(self, task):
		self.tasks.append(task)
	
	def run_until_complete(self):
		loop = asyncio.get_event_loop()
		try:
			for task in self.tasks:
				asyncio.ensure_future(task)
			# This is for when a KeyboardInterupt happens inside a @keyboard_interuptable_loop_coroutine
			# this will more likely happen when there is more work to do in side the worker coroutines (some slight blocking)
			loop.run_until_complete(keep_running_till_all_others_complete(loop)) 
		except KeyboardInterrupt as kbi:
			print('KeyboardInterupt in main function')
			if self.close is not True:
				self.close = True
				# This is for when a KeyboardInterupt happens inside a the "loop.run_forever/loop.run_until_complete" coroutine
				# This will more likely happen when there is very little work to be done (almost no blocking)
				loop.run_until_complete(keep_running_till_all_others_complete(loop))
	
	
	
	


class Window:
	"""
		represents a window space on the screen that you can place text in
	"""
	contents = None
	def __init__(self, parent, height=-1, width=-1, y_start=0, x_start=0):
		if height == -1:
			height = parent.getmaxyx()[0]
		if width == -1:
			width = parent.getmaxyx()[1]
			
		self.parent = parent
		self.parent.nodelay(True)
		self.text_area = self.parent.derwin(height, width, y_start, x_start)
		self.text_area.scrollok(True)
		self.text_area.nodelay(True)
		self.Contents = ''

	@property
	def contents(self):
		''' getter for contents (mainly ment to create a property for the following setter)'''
		return self.Contents
	
	@contents.setter
	def contents(self, value):
		''' setter for contests of the text area '''
		self.clear_text()
		self.Contents = str(value)
		self.text_area.addstr(0,0, self.Contents)
		self.text_area.noutrefresh()

	def add(self, text, color=DEFAULT_COLOR):
		self.text_area.addstr(text, curses.color_pair(color))
		self.text_area.noutrefresh()
		
	
	def clear_text(self):
		''' clears the window '''
		# this is probobly a bit of a hack but ...
		#	self.text_area.clear() makes everything blink
		maxy, maxx = self.text_area.getmaxyx()
		self.text_area.addstr(0,0, ' '*maxy*maxx)
		self.text_area.noutrefresh()
		
	@property
	def maxyx(self):
		return self.text_area.getmaxyx()

class BaseUI1:
	'''
		a class that represents the UI and is used as the base for specific UIs
	'''
	def __init__(self, rate=1):
		'''
			creates the UI and sets it's fram rate.
		'''
		
		self.rate = rate
		self.close = False
		
		
	def __enter__(self):
		'''
			initalizes this UI for use in context managers
		'''
		#self.main_window = curses.initscr()
		#self.main_window.nodelay(True)
		#self.main_window.keypad(True)
		#curses.noecho()
		#curses.start_color()
		self.setup()
		return self
		
	def setup(self):
		'''
			this is where you create all the sub windows/etc for the class
		'''
		pass
		
	def cleanup(self):
		'''
			this is where you do any special clean up when closing down your UI
		'''
		pass
		
	def __exit__(self, *args):
		'''
			used to return the consle back to normal after leaving the context
		'''
		curses.nocbreak()
		curses.endwin()


	def keyboard_interuptable_loop_coroutine(f):
		async def func_wrapper(*args, **kwargs):
			self = args[0]
			print(self)
			while self.close == False:
				await asyncio.sleep(0)
				try:
					await f(*args, **kwargs)
				except KeyboardInterrupt as kbi:
					self.cleanup()
					self.close = True
		return func_wrapper

	@property
	def maxyx(self):
		return self.main_window.getmaxyx()
	
	
	async def screen_updater(self):
		'''
			a Job that is used to refresh the screen at the specified frame rate
		'''
		await asyncio.sleep(self.rate)
		self.pre_update_work()
		#curses.doupdate()
		
	def pre_update_work(self):
		pass
	
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


	
	
	
	
	
	
	
	
	
class TestUI_1(TaskLoopBase):
	@keyboard_interuptable_loop_coroutine
	async def test1(self, name):
		await asyncio.sleep(1)
		#time.sleep(1)
		print(f'running test 1 {name}')
		
class TestUI_2(TaskLoopBase):
	@keyboard_interuptable_loop_coroutine
	async def test1(self, name):
		#await asyncio.sleep(1)
		time.sleep(1)
		print(f'running test 1 {name}')	
		
		
	
			
			




def tests():
	print('starting')
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
