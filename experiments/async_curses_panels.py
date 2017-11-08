import asyncio
import curses


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

class BaseUI:
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
		self.main_window = curses.initscr()
		self.main_window.nodelay(True)
		self.main_window.keypad(True)
		curses.noecho()
		curses.start_color()
		

		

		
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
		while True:
			try:
				await asyncio.sleep(self.rate)
				if self.close:
					return
				else:
					self.pre_update_work()
					curses.doupdate()
			except KeyboardInterrupt:
				self.cleanup()
				self.close = True
	
	def pre_update_work(self):
		pass
	
	async def keyboard_listener(self):
		while True:
			key = await self.get_key()
			if key is None:
				continue
			else:
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

def tests():
	pass


if __name__=='__name__':
	tests()
