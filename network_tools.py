import asyncio
import ipaddress


async def run_command(*args):
	process = await asyncio.create_subprocess_exec( *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
	stdout, stderr = await process.communicate()
	out = stdout.decode().strip()
	error = stderr.decode().strip()
	return (out, error)

async def ping(host):
	return await run_command('ping', '-c', '1', '-W', '1', host)


async def ping_scan(network):
	for host in ipaddress.ip_network(network):
		out, error = await ping(str(host))
	return (out, error)
	

def run_test():
	

	loop = asyncio.get_event_loop()
	commands = asyncio.gather(ping('google.com'), ping('10.10.1.1'), ping_scan('10.10.1.0/24'))
	# Run the commands
	results = loop.run_until_complete(commands)
	# Print a report
	for result in results:
		print("STD OUT")
		print(result[0])
		print("STD ERROR")
		print(result[1])
	loop.close()

if __name__=='__main__':
	run_test()
