import asyncio
import curses
import random

import async_curses

import time

DEFAULT = 1 # DEFAULT_COLOR
RED = 2
GREEN = 3

SELECT_DEFAULT = 11
SELECT_RED = 12
SELECT_GREEN = 13

BLACK_BACKGROUND = 0
WHITE_BACKGROUND = 1 

class HostInfoWindow(async_curses.Window):
	def __init__(self, parent, height=-1, width=-1, y_start=0, x_start=0):
		super().__init__(parent, height, width, y_start, x_start)
		self.Active = False
		self.Lable = ''
		self.State = ''
		
	@property
	def active(self):
		return self.Active
	
	@active.setter
	def active(self, value):
		old = self.active
		if value == True or value == False:
			self.Active = value
		if self.active != old:
			self.update_contents()
	
	@property
	def lable(self):
		return self.Lable
		
	@lable.setter
	def lable(self, value):
		old = self.Lable
		self.Lable = str(value)
		if self.lable != old:
			self.update_contents()
	
	@property
	def state(self):
		return self.State
		
	@state.setter
	def state(self, value):
		old = self.state
		if value == 'UP' or value == 'DOWN':
			self.State = value
		if self.state != old:
			self.update_contents()
		
		
	def update_contents(self):
		self.clear_text()
		
		if self.active:
			self.add(self.lable+":", color=SELECT_DEFAULT)
			if self.state == 'UP':
				self.add(self.state, color=SELECT_GREEN)
			else:
				self.add(self.state, color=SELECT_RED)
		
		else:
			self.add(self.lable+":", color=DEFAULT)
			if self.state == 'UP':
				self.add(self.state, color=GREEN)
			else:
				self.add(self.state, color=RED)	
		self.text_area.noutrefresh()



class UI(async_curses.BaseUI):
	def setup(self):
		curses.init_pair(DEFAULT, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(RED, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
		
		
		
		curses.init_pair(SELECT_DEFAULT, curses.COLOR_CYAN, curses.COLOR_WHITE)
		curses.init_pair(SELECT_RED, curses.COLOR_RED, curses.COLOR_WHITE)
		curses.init_pair(SELECT_GREEN, curses.COLOR_GREEN, curses.COLOR_WHITE)
		
		maxy, maxx = self.maxyx
		self.title = async_curses.BorderedWindow(self.main_window, 3, maxx, 0, 0)
		title_text = "Network 10.10.1.0/24"
		num_spaces = (maxx -2 - len(title_text))//2
		self.title.contents = ' '*num_spaces + title_text
		self.body = async_curses.BorderedWindow(self.main_window, maxy - 3, maxx, 3, 0)
		self.rows = 43
		self.cols = 6
		
		self.layout = async_curses.TableLayout(self.body.text_area, self.rows, self.cols, HostInfoWindow)
		self.active_cell = [0,0]
		
		
	async def worker(self):
		try:
			while True:
				await asyncio.sleep(0.01)
				r = random.randint(0, self.rows-1)
				c = random.randint(0, self.cols-1)
				num = r + c*self.rows
				randvalue = random.choice(['UP', 'DOWN'])
				textarea = self.layout.sub_windows[r][c]
				if self.close:
					return
				if num<=255:
					textarea.lable = str(num)
					textarea.state = randvalue
					
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return
			
	def key_stroke_handler(self, key):
		last_active = self.layout.sub_windows[self.active_cell[0]][self.active_cell[1]]
		last_active.active = False
		
		if key == curses.KEY_UP:
			self.active_cell[0] -= 1
			if self.active_cell[0] < 0:
				self.active_cell[0] = 0
				
		elif key == curses.KEY_DOWN:
			self.active_cell[0] += 1
			if self.active_cell[0] > self.rows - 1:
				self.active_cell[0] = self.rows - 1
				
		elif key == curses.KEY_RIGHT:
			self.active_cell[1] += 1
			if self.active_cell[1] > self.cols -1:
				self.active_cell[1] = self.cols -1
			
		elif key == curses.KEY_LEFT:
			self.active_cell[1] -= 1
			if self.active_cell[1] < 0:
				self.active_cell[1] = 0
			
		current_active = self.layout.sub_windows[self.active_cell[0]][self.active_cell[1]]
		current_active.active = True

if __name__=='__main__':
	try:
		with UI(frame_rate=10) as ui:
			loop = asyncio.get_event_loop()
			asyncio.ensure_future(ui.worker())
			asyncio.ensure_future(ui.keyboard_listener())
			loop.run_until_complete(ui.screen_updater())
	except KeyboardInterrupt:
		pass
