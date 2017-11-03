import asyncio
from collections import namedtuple

CommandResult = namedtuple('CommandResult', ['command', 'out', 'error'])

async def run_command_str(command_string):
	split_string = command_string.split(' ')
	return await run_command(*split_string)
	

async def run_command(*args):
	process = await asyncio.create_subprocess_exec( *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
	stdout, stderr = await process.communicate()
	out = stdout.decode().strip()
	error = stderr.decode().strip()
	return CommandResult(args, out, error)
	
	
def command_to_string(command):
	command_string = ''
	for part in command:
		if command_string != '':
			command_string += ' '
		command_string += part
		
	return command_string
	

def print_command(command):
	print(command_to_string(command))
	
	
def print_result(result):
	print('=============================================')
	print(f'COMMAND:{command_to_string(result.command)}')
	if result.out != '':
		print('STDOUT')
		print(result.out)
	if result.error != '':
		print('STDERROR')
		print(result.error)
	print('=============================================')
