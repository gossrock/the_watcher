import asyncio
import typing
from typing import NamedTuple, List

class CommandResult(NamedTuple):
	command:List[str]
	out:str
	error:str

async def run_command_str(command_string:str) -> CommandResult:
	split_string = command_string.split(' ')
	return await run_command(split_string)
	

async def run_command(command:List[str]) -> CommandResult:
	try:
		process = await asyncio.create_subprocess_exec( *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
	except FileNotFoundError as e:
		return CommandResult(command, '', str(e))
	stdout, stderr = await process.communicate()
	out:str = stdout.decode().strip()
	error:str = stderr.decode().strip()
	return CommandResult(command, out, error)
	
	
def command_to_string(command:List[str]) -> str:
	command_string = ''
	for part in command:
		if command_string != '':
			command_string += ' '
		command_string += part
		
	return command_string
	

def print_command(command:List[str]) -> None:
	print(command_to_string(command))
	
	
def print_result(result:CommandResult) -> None:
	print('=============================================')
	print(f'COMMAND:{command_to_string(result.command)}')
	if result.out != '':
		print('STDOUT')
		print(result.out)
	if result.error != '':
		print('STDERROR')
		print(result.error)
	print('=============================================')


if __name__=='__main__':
	loop = asyncio.get_event_loop()
	results = loop.run_until_complete(run_command_str('ls -la'))
	print_result(results)
	
	results = loop.run_until_complete(run_command_str('ping -c 1 firewall'))
	print_result(results)

	results = loop.run_until_complete(run_command_str('ping -c 1 192.168.0.1'))
	print_result(results)

	results = loop.run_until_complete(run_command_str('not a command'))
	print_result(results)
