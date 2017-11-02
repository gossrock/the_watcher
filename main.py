import asyncio
import curses
import random
import math

import async_curses
import network_tools

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
		elif value == network_tools.STATE_UP:
			self.State = 'UP'
		elif value == network_tools.STATE_DOWN:
			self.State = 'DOWN'
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
		self.ping_results = {}
			
	async def ping_worker(self, rate):
		tasks = []
		num = 0
		while True:
			await asyncio.sleep(rate)
			task = asyncio.ensure_future(network_tools.ping(f'10.10.8.{num}'))
			tasks.append(task)
			
			#check for results
			for task in tasks:
				await asyncio.sleep(0)
				if task.done():
					tasks.remove(task)
					result = task.result()
					result = network_tools.parse_ping_output(*result)
					ip_num = None
					if result.ip is not None:
						ip_num = int(result.ip.split('.')[3])
					else:
						continue
					c = math.floor(ip_num/self.rows)
					r = ip_num % self.rows
					
					textarea = self.layout.sub_windows[r][c]
					textarea.lable = str(ip_num)
					textarea.state = result.state
			num += 1
			if num > 255:
				num = 0
					
			
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
			asyncio.ensure_future(ui.keyboard_listener())
			asyncio.ensure_future(ui.ping_worker(0.1))
			loop.run_until_complete(ui.screen_updater())
	except KeyboardInterrupt:
		pass
