import asyncio
import random

import async_curses

class UI(async_curses.BaseUI):
	def setup(self):
		self.rows = 52
		self.cols = 5
		self.layout = async_curses.TableLayout(self.main_window, self.rows, self.cols)
		
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
				if num<255:
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
