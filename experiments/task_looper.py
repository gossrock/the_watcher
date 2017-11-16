import asyncio


#For typing
from typing import Callable, Set, List, NamedTuple
from asyncio import Task
from asyncio.events import AbstractEventLoop

#For Testing
import time



# Helper functions
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

# function decorator that creates an infinate loop that exits nicely with Ctrl-C
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




# The main thing
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
