import asyncio
import curses
import random
import math
import ipaddress

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
		self.PingResults = None
		self.lable = '-:'
		self.lable_color = DEFAULT
		self.info = 'Unknown'
		self.info_color = RED
	
	@property
	def ping_results(self):
		return 
	
	@ping_results.setter
	def ping_results(self, value):
		# get the colors
		self.lable_color = DEFAULT
		self.info_color = DEFAULT
		if self.active:
			self.lable_color = SELECT_DEFAULT
			self.info_color = SELECT_DEFAULT
			if value.state == network_tools.STATE_UP:
				self.info_color = SELECT_GREEN
			else:
				self.info_color = SELECT_RED
				
		else:
			if value.state == network_tools.STATE_UP:
				self.info_color = GREEN
			else:
				self.info_color = RED
		
		self.lable = '-:'
		host = ''
		if value.state == network_tools.STATE_UP:
			host = 'Unknown'
		r_dns = None
		if value.ip is not None:
			self.lable = value.ip.split('.')[3] + ':'
			r_dns = network_tools.reverse_dns(value.ip)
			if r_dns is not None:
				host = r_dns.split('.')[0]
			width = self.maxyx[1] - 5
			if len(host)>width:
				host = host[0:width-1]
				
		self.info = host
		
		self.update_contents()
		
		
		
	
	@property
	def active(self):
		return self.Active
	
	@active.setter
	def active(self, value):
		if value == True or value == False:
			self.Active = value
			if self.active == True:
				self.lable_color = SELECT_DEFAULT
				if self.info_color == RED:
					self.info_color = SELECT_RED
				elif self.info_color == GREEN:
					self.info_color = SELECT_GREEN
			else:
				self.lable_color = DEFAULT
				if self.info_color == SELECT_RED:
					self.info_color = RED
				elif self.info_color == SELECT_GREEN:
					self.info_color = GREEN	
			self.update_contents()
		
	def update_contents(self):
		self.clear_text()
		self.add(self.lable, color=self.lable_color)
		self.add(self.info, color=self.info_color)
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
		title_text = "Network:"
		num_spaces = (maxx -2 - len(title_text))//2
		self.title.contents = ' '*num_spaces + title_text
		self.body = async_curses.BorderedWindow(self.main_window, maxy - 3, maxx, 3, 0)
		self.rows = 43
		self.cols = 6
		
		self.layout = async_curses.TableLayout(self.body.text_area, self.rows, self.cols, HostInfoWindow)
		
		self.active_cell = [0,0]
		self.ping_results = {}
	
	def set_title(self, network_address):
		maxy, maxx = self.maxyx
		title_text = f'Network: {network_address}'
		num_spaces = (maxx -2 - len(title_text))//2
		self.title.contents = ' '*num_spaces + title_text
	
	async def ping_worker(self, network, rate):
		tasks = []
		while True:
			for address in network:
				await asyncio.sleep(rate)
				address_str = str(address)
				task = asyncio.ensure_future(network_tools.ping(address_str))
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
						textarea.ping_results = result
			
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
			network_info = loop.run_until_complete(network_tools.get_default_nework_info())
			network_address = ipaddress.IPv4Network(network_info.network_address)
			ui.set_title(str(network_address))
			
			asyncio.ensure_future(ui.keyboard_listener())
			asyncio.ensure_future(ui.ping_worker(network_address, 0.1))
			loop.run_until_complete(ui.screen_updater())
	except KeyboardInterrupt:
		pass
