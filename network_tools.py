import asyncio
import ipaddress
import socket

from collections import namedtuple

from command_execution import run_command, run_command_str, print_result

#### DEFAULT NETWORK ####
async def get_default_nework_info():
	command_results = await run_command_str('ip route show')
	# if there is a default route this command will return something like:
	
	# default via 192.168.0.1 dev wlan0
	
	# on the first line.
	# if there isn't a default route this first line will be missing 
	
	# on each of the following lines there is something like this for each interface
	#192.1168.0.0/24 dev wlan0 proto kernel scope link src 192.168.0.100 metric 600 
	gateway = None
	interface_name = None
	network_address = None
	host_address = None
	
	result_lines = command_results.out.split('\n')
	words = result_lines[0].split(' ') 
	
	
	if words[0] == 'default': # it has a default route.
		gateway = words[2] # this is the gateway address
		interface_name = words[4] #this is the name of the interface that is on the network that the default gateway is on
	else:
		return None #there is no default so quit here because we are not on-line.
		
	for line in result_lines:
		words = line.split(' ')
		if words[2] == interface_name: 
			# if word[2] is the same interface as the name on the default line 
			# then this line is the one that contains the address information
			# for the network that we will want to use for scanning etc
			
			# the 0th 'word' is the network CIDR address
			network_address = words[0] 
			# the 8th (though I'm afraid it isn't always the 8th) 
			# is the computers ip address on that network 
			host_address = words[8] 
	print( (interface_name, network_address, gateway, host_address, ))
				


#### REVERSE DNS ####
def reverse_dns(ip):
	if ip is not None:
		try:
			return socket.gethostbyaddr(ip)[0]
		except socket.herror:
			return None
	else:
		return None


#### PING ####
PingResults = namedtuple('PingResults', ['host', 'ip', 'state', 'time', 'error'])

async def ping(host):
	return await run_command('ping', '-c', '1', '-W', '1', host)

#### PARSE PING RESULTS ####
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
	r_dns = None
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
		
	if ip_of_what_was_pinged is not None and up_or_down == STATE_UP:
		r_dns = reverse_dns(ip_of_what_was_pinged)
	
	return PingResults(host=what_was_pinged, ip=ip_of_what_was_pinged, 
						state=up_or_down, time=ping_time, error=error_type)


#### PRINT PING RESULTS ####
def print_ping_results(results):
	if results.state == STATE_UP:
		print(f'\r{results.ip}\t{results.time}ms\t{reverse_dns(results.ip)}\t IS UP')
	else:
		if results.error != ERROR_DOWN and results.error != ERROR_BRODCAST:
			print(f'\r{results.ip}**********\t\terror on {results.ip},{reverse_dns(results.ip)} ({results.error})')
		else:
			print(f'\r{results.ip}\t{reverse_dns(results.ip)}\t IS DOWN')


#### PING SCAN ####
async def ping_scan(network):
	results = []
	tasks = []
	for host in ipaddress.ip_network(network):
		await asyncio.sleep(0)
		task = asyncio.ensure_future(ping(str(host)))
		tasks.append(task)
		
	for task in tasks:
		while True:
			await asyncio.sleep(0)
			if task.done():
				result = task.result()
				results.append(task.result())
				break
	return results
	
	
	



#### TESTS ####
def run_test():
	loop = asyncio.get_event_loop()
	
	'''
	#test 1
	result = loop.run_until_complete(ping('10.10.1.1'))
	print_result(result)
	
	
	#test 2
	result = loop.run_until_complete(ping('google.com'))
	print_result(result)
	
	#test 3
	results = loop.run_until_complete(ping_scan('10.10.8.0/24'))
	
	# Print a report
	for result in results:
		print_result(result)
		print(parse_ping_output(*result))
	
	for result in results:
		parsed_results = parse_ping_output(*result)
		#if parsed_results.state == STATE_UP:
		print_ping_results(parsed_results)
	'''
	# testing local interface function
	results = loop.run_until_complete(get_default_nework_info())
	loop.close()



if __name__=='__main__':
	run_test()
