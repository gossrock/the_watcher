import asyncio
import random

import async_curses

class UI(async_curses.BaseUI):
	def setup(self):
		maxy, maxx = self.maxyx
		self.title = async_curses.BorderedWindow(self.main_window, 3, maxx, 0, 0)
		title_text = "Network 10.10.1.0/24"
		num_spaces = (maxx -2 - len(title_text))//2
		self.title.contents = ' '*num_spaces + title_text
		self.body = async_curses.BorderedWindow(self.main_window, maxy - 3, maxx, 3, 0)
		self.rows = 43
		self.cols = 6
		self.layout = async_curses.TableLayout(self.body.text_area, self.rows, self.cols)
		
	async def worker(self):
		try:
			while True:
				await asyncio.sleep(0.01)
				r = random.randint(0, self.rows-1)
				c = random.randint(0, self.cols-1)
				num = r + c*self.rows
				randvalue = random.randint(1, 999)
				textarea = self.layout.sub_windows[r][c]
				if self.close:
					return
				if num<=255:
					textarea.contents = f'{num}: {randvalue}'
		except KeyboardInterrupt:
			self.cleanup()
			self.close = True
			return

if __name__=='__main__':
	try:
		with UI() as ui:
			loop = asyncio.get_event_loop()
			asyncio.ensure_future(ui.worker())
			loop.run_until_complete(ui.screen_updater())
	except KeyboardInterrupt:
		pass
