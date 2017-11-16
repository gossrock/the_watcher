import asyncio
import curses
from abc import ABC

from task_looper import TaskLoopBase, keyboard_interuptable_loop_coroutine

class BaseUI(ABC, TaskLoopBase):
	pass
	
class BaseScreen(ABC):
	pass
	
class TextArea:
	pass


if __name__ == '__main__':
	print('first test')

