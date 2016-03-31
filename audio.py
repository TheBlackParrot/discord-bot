# I can't figure out a queue system, nor can I figure out asyncio.
'''
import threading;

class VoiceSystem():
	def __init__(self):
		self.checkToMoveOn();

		self.times = 0;

		self.queue = VoiceQueue();

	def checkToMoveOn(self):
		self.times += 1;
		print(self.times);

		self.timer = threading.Timer(3.0, self.checkToMoveOn);
		self.timer.start();
'''

class VoiceQueue():
	def __init__(self):
		self.queue = [];

	def queue(self, url, userid):
		if not userid or not url:
			return;

		dict = {};
		dict["submitter"] = userid;
		dict["url"] = url;

		self.queue.append(dict);

		return dict;

	def unqueue(self, url, userid=None, override=False):
		if (not userid and not override) or not url:
			return None;

		for i in range(0, len(self.queue)):
			dict = self.queue[i];

			if dict["url"] == url:
				removed = self.queue.pop(i);
				return removed;

		return None;

	def __len__(self):
		return len(self.queue);

	def __getitem__(self, value):
		if value > len(self.queue):
			return None;

		return self.queue[value];

	def getNext(self, remove=False):
		if remove:
			return self.queue.pop(0);

		return self.queue[0];