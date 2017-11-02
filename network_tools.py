import asyncio
import ipaddress
import socket

from collections import namedtuple

from command_execution import *



PingResults = namedtuple('PingResults', ['host', 'ip', 'reverse_dns', 'state', 'time', 'error'])


	







async def ping(host):
	return await run_command('ping', '-c', '1', '-W', '1', host)


STATE_UP = True
STATE_DOWN = False
NO_ERROR_UP = ' 0% packet loss'
ERROR_DOWN = '100% packet loss'
ERROR_UNKNOWN = 'unknown host'
ERROR_NO_NETWORK = 'Network is unreachable'
ERROR_BRODCAST = 'Do you want to ping broadcast?'
ERROR_BRODCAST_MSG = 'brodcast address ping'
def parse_ping_output(command, out, error):
	what_was_pinged = None
	ip_of_what_was_pinged = None
	reverse_dns = None
	up_or_down = None
	ping_time = None
	error_type = None
	
	if out!='': # if out has something
		splitout = out.split('\n')
		split_line_1 = splitout[0].split(' ')
		what_was_pinged = split_line_1[1]
		ip_of_what_was_pinged = split_line_1[2][1:-1] 
		if ERROR_DOWN in out:
			up_or_down = STATE_DOWN
			error_type = ERROR_DOWN
		elif NO_ERROR_UP in out:
			up_or_down = STATE_UP
			ping_time = splitout[1].split(" ")[-2].split('=')[1]
		#print(out)
		
	if error!='': # if error has something
		if ERROR_UNKNOWN in error:
			error_type = ERROR_UNKNOWN
			what_was_pinged = error.split(' ')[3][0:-1]
		
		elif ERROR_NO_NETWORK in error:
			error_type = ERROR_NO_NETWORK
		elif ERROR_BRODCAST in error:
			error_type = ERROR_BRODCAST_MSG
		else: # for unknown errors
			error_type = error
		
	if ip_of_what_was_pinged is not None:
		try:
			reverse_dns = socket.gethostbyaddr(ip_of_what_was_pinged)[0]
		except:
			pass
	
	return PingResults(host=what_was_pinged, ip=ip_of_what_was_pinged, reverse_dns=reverse_dns, 
						state=up_or_down, time=ping_time, error=error_type)


def print_ping_results(results):
	if results.state == STATE_UP:
		print(f'\r{results.ip}\t{results.time}ms\t{results.reverse_dns}\t IS UP')
	else:
		if results.error != ERROR_DOWN and results.error != ERROR_BRODCAST:
			print(f'\r{results.ip}**********\t\terror on {results.ip},{results.reverse_dns} ({results.error})')
		else:
			print(f'\r{results.ip}\t{results.reverse_dns}\t IS DOWN')


async def ping_scan(network):
	results = []
	tasks = []
	for host in ipaddress.ip_network(network):
		await asyncio.sleep(0)
		print(f'pinging {host}')
		task = asyncio.ensure_future(ping(str(host)))
		tasks.append(task)
		
	for task in tasks:
		while True:
			await asyncio.sleep(0)
			if task.done():
				result = task.result()
				print(f'finished: {result.command}')
				results.append(task.result())
				break
	return results
	

def run_test():
	loop = asyncio.get_event_loop()
	
	#test 1
	result = loop.run_until_complete(ping('10.10.1.1'))
	print_result(result)
	
	
	#test 2
	result = loop.run_until_complete(ping('google.com'))
	print_result(result)
	
	#test 3
	results = loop.run_until_complete(ping_scan('10.10.32.0/24'))
	
	# Print a report
	for result in results:
		print_result(result)
		print(parse_ping_output(*result))
	
	for result in results:
		parsed_results = parse_ping_output(*result)
		if parsed_results.state == STATE_UP:
			print_ping_results(parsed_results)
	
		
	loop.close()

if __name__=='__main__':
	run_test()
