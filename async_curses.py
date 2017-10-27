import asyncio
import curses

import random
import math

WHITE = 1
RED = 2
GREEN = 3

class Window:
	"""
		represents a window space on the screen that you can place text in
	"""
	contents = None
	def __init__(self, parent, height, width, y_start, x_start):
		self.parent = parent
		self.text_area = self.parent.derwin(height, width, y_start, x_start)
		self.text_area.scrollok(True)
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

	def add(self, text, color=WHITE):
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


class BorderedWindow(Window):
	'''
		a sub class of Window that simply has a border around it.
	'''
	def __init__(self, parent, height, width, y_start, x_start):
		self.parent = parent
		self.border = self.parent.derwin(height, width, y_start, x_start)
		self.border.box()
		self.border.noutrefresh()
		self.text_area = self.parent.derwin(height-2, width-2, y_start+1, x_start+1)
		self.text_area.scrollok(True)
		self.Contents = ''


class TableLayout:
	'''
		used to create multiple windows of a spectified type that are equaly spaced
		into the given number of rows and cols. I have it as a class but it may
		be better to change it to simply a function that returns a '2d' list.
	'''
	def __init__(self, parent, rows, cols, window_type=Window):
		self.parent = parent
		self.sub_windows = [ [ None for i in range(cols) ] for j in range(rows) ]
		maxy, maxx = self.parent.getmaxyx()
		height = math.floor(maxy/rows)
		width = math.floor(maxx/cols)
		y_start = 0
		x_start = 0
		for row_num in range(rows):
			y_start = height*row_num
			for col_num in range(cols):
				x_start = width*col_num
				self.sub_windows[row_num][col_num] = window_type(self.parent, height, width, y_start, x_start)
		


class BaseUI:
	'''
		a class that represents the UI and is used as the base for specific UIs
	'''
	def __init__(self, frame_rate=1):
		'''
			creates the UI and sets it's fram rate.
		'''
		
		self.frame_rate = frame_rate
		self.close = False
		
		
	def __enter__(self):
		'''
			initalizes this UI for use in context managers
		'''
		self.main_window = curses.initscr()
		curses.start_color()
		curses.init_pair(WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(RED, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)

		self.main_window.nodelay(True)
		self.main_window.keypad(True)
		curses.noecho()
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

	@property
	def maxyx(self):
		return self.main_window.getmaxyx()

	async def screen_updater(self):
		'''
			a Job that is used to refresh the screen at the specified frame rate
		'''
		try:
			while True:
				await(asyncio.sleep(1/self.frame_rate))
				if self.close:
					return
				else:
					curses.doupdate()
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return
		
			
		


class TestingUI_1(BaseUI):
	'''
		My first test creates a single border window and randomly changes the message in it.
	'''
	def setup(self):
		maxy, maxx = self.main_window.getmaxyx()
		self.textarea = BorderedWindow(self.main_window, maxy, maxx, 0, 0)

	async def test_worker(self):
		try:
			while True:
				await asyncio.sleep(0)
				if self.close:
					return
				messages = ['this is a test', 
						'this is really a test', 
						'another',
						'test']
				self.textarea.contents = random.choice(messages)
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return

class TestingUI_2(BaseUI):
	'''
		My second test creates 2 non bordered windows and randomly places messages in each
	'''
	def setup(self):
		maxy, maxx = self.main_window.getmaxyx()
		self.textarea1 = Window(self.main_window, math.floor(maxy/2), maxx, 0, 0)
		self.textarea2 = Window(self.main_window, math.floor(maxy/2), maxx, math.floor(maxy/2), 0)
			
	async def test_worker_1(self):
		try:
			while True:
				await asyncio.sleep(0)
				if self.close:
					return
				messages = ['this is a test', 
						'this is really a test', 
						'another',
						'test']
				self.textarea1.contents = random.choice(messages)+" "+str(random.randint(0, 99999))
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return
	
	
	async def test_worker_2(self):
		try:
			while True:
				await asyncio.sleep(0)
				if self.close:
					return
				messages = ['this is a test', 
						'this is really a test', 
						'another',
						'test']
				self.textarea2.contents = random.choice(messages)+" "+str(random.randint(0, 99999))
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return		


class TestingUI_3(BaseUI):
	'''
		my third test that creates a 2 rows of 3 windows that are borderd and randomly 
		selects a window and changes it's text.
	'''
	def setup(self):
		self.rows = 2
		self.cols = 3
		self.layout = TableLayout(self.main_window, self.rows, self.cols, BorderedWindow)
	
	async def test_worker(self):
		try:
			while True:
				await asyncio.sleep(0.01)
				r = random.randint(0, self.rows-1)
				c = random.randint(0, self.cols-1)
				textarea = self.layout.sub_windows[r][c]
				if self.close:
					return
				messages = ['this is a test', 
						'this is really a test', 
						'another',
						'test',
						'this is a really really long test to see what happens when it gets to the end of the line']
				textarea.contents = random.choice(messages)
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return
		

def run_testing_ui():
	try:
		with TestingUI_1(frame_rate=1) as ui:
			loop = asyncio.get_event_loop()
			asyncio.ensure_future(ui.test_worker())
			loop.run_until_complete(ui.screen_updater())
		
		with TestingUI_2(frame_rate=1) as ui:
			loop = asyncio.get_event_loop()
			asyncio.ensure_future(ui.test_worker_1())
			asyncio.ensure_future(ui.test_worker_2())
			loop.run_until_complete(ui.screen_updater())
			
		with TestingUI_3(frame_rate=1) as ui:
			loop = asyncio.get_event_loop()
			asyncio.ensure_future(ui.test_worker())
			loop.run_until_complete(ui.screen_updater())
	except KeyboardInterrupt:
		print('ending program')
		

if __name__=='__main__':
	run_testing_ui()
