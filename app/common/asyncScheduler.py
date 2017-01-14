import asyncio

class asyncScheduler(object):
	def __init__(self, interval, function, loop):
		self.interval = interval
		self.loop = loop
		self.function = function
		self.running = [];

		self.scheduleNextCall()

	async def run(self):
		await asyncio.sleep(self.interval, loop=self.loop)
		self.scheduleNextCall()
		await self.loop.run_in_executor(None, self.function)

	def scheduleNextCall(self):
		asyncio.ensure_future(self.run(), loop=self.loop)
