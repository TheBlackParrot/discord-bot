import time;

class PingPong():
	def __init__(self):
		self.before = int(round(time.time() * 1000));
		self.after = None;
		self.msgObj = None;

	def pong(self):
		self.after = int(round(time.time() * 1000));

	def __int__(self):
		if not self.after:
			return -1;

		return self.after - self.before;