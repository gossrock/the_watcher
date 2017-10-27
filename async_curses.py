import asyncio
import curses

import random


class BorderedWindow:
	def __init__(self, parent, height, width, y_start, x_start):
		self.parent = parent
		self.border = self.parent.derwin(height, width, y_start, x_start)
		self.border.box()
		self.border.noutrefresh()
		self.text_area = self.parent.derwin(height-2, width-2, 1,1)
		self.text_area.scrollok(True)
	
	@property
	def contents(self):
		return self.Contents
	
	@contents.setter
	def contents(self, value):
		self.clear_text()
		self.Contents = str(value)
		self.text_area.addstr(0,0, self.Contents)
		self.text_area.noutrefresh()

	def clear_text(self):
		maxy, maxx = self.text_area.getmaxyx()
		self.text_area.addstr(0,0, ' '*maxy*maxx)
		self.text_area.noutrefresh()

class BaseUI:
	def __init__(self, frame_rate=10):
		self.frame_rate = frame_rate
		self.close = False
		
		
	def __enter__(self):
		self.main_window = curses.initscr()
		
		self.main_window.nodelay(True)
		self.main_window.keypad(True)
		curses.noecho()
		self.setup()
		return self
		
	def setup(self):
		pass
		
	def cleanup(self):
		pass
		
	def __exit__(self, *args):
		curses.nocbreak()
		curses.endwin()


	async def screen_updater(self):
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
	def setup(self):
		maxy, maxx = self.main_window.getmaxyx()
		self.textarea = BorderedWindow(self.main_window, maxy, maxx, 0, 0)

	async def test_worker(self):
		try:
			while True:
				await asyncio.sleep(0)
				if self.close:
					return
				messages = [	'this is a test', 
						'this is really a test', 
						'another',
						'test'
					]
				self.textarea.contents = random.choice(messages)
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return
			
			
			

def run_testing_ui():
	with TestingUI_1(frame_rate=1) as ui:
		loop = asyncio.get_event_loop()
		asyncio.ensure_future(ui.test_worker())
		loop.run_until_complete(ui.screen_updater())
			
	#print('ending program')
		

if __name__=='__main__':
	run_testing_ui()
