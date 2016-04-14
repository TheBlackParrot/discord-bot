import functools;
import youtube_dl;
import asyncio;

class VoiceSettings():
	def __init__(self):
		self.volume = 0.66;
		self.tempo = 1;
		self.pitch = 1;
		self.rate = 44100;

	def __str__(self):
		filters = [];

		filters.append("volume=" + str(self.volume));
		filters.append("atempo=" + str(self.tempo / self.pitch));
		filters.append("asetrate=" + str(self.pitch * self.rate));

		return '-af "' + ','.join(filters) + '"';

	def update(self, setting, value):
		if setting == "pitch":
			self.pitch = max(0.25, min(value, 3));
			return self.pitch;

		if setting == "tempo":
			self.tempo = max(0.5, min(value, 2));
			return self.tempo;

		if setting == "volume":
			self.volume = max(0.05, min(value, 3));
			return self.volume;

		if setting == "rate":
			self.rate = value;

		return False;

def getYTDLInfo(url, get_format=True):
	# this wouldn't be here if i could just access acodec from create_ytdl_player
	# youtube-dl doesn't sort formats correctly anyways so maybe this is better anyhow
	# (you'll usually get 50kbps opus from the first result, try it)

	opts = {
		'format': 'bestaudio/webm[abr<128]/best'
	}

	ydl = youtube_dl.YoutubeDL(opts)
	info = ydl.extract_info(url, download=False);

	formats = info.pop("formats");

	best = {
		"bitrate": 0,
		"id": 0
	};

	out = {"info": info};

	if formats:
		for i in range(0, len(formats)):
			format = formats[i];

			if "abr" not in format:
				continue;

			if format["vcodec"] == "none":
				if int(format["abr"]) > best["bitrate"]:
					best["bitrate"] = int(format["abr"]);
					best["id"] = i;

		out["format"] = formats[best["id"]];

	return out;

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
'''