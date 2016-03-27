import random;
import os;

import settings as setting;

class Corpus():
	def __init__(self, filename=setting.CORPUS_FILENAME):
		self.corpus = {};
		self.filesize = 0;
		self.filename = filename;

		self.load();

	def load(self):
		with open(self.filename, 'r', encoding="utf-8") as file:
			self.filesize = os.path.getsize(self.filename);

			for line in file:
				if line:
					self.add(line);

	def add(self, line):
		corpus = self.corpus;

		words = line.split();

		if len(words) < 2:
			return;

		phrase = words[0] + " " + words[1];

		if len(words) == 2:
			if phrase not in corpus:
				corpus[phrase] = [];

			return;

		nextWord = words[2];

		for i in range(1, len(words)):
			if phrase not in corpus:
				corpus[phrase] = [];

			if not nextWord:
				continue;

			corpus[phrase].append(nextWord);

			phrase = words[i] + " " + words[i+1];

			if i+2 < len(words):
				nextWord = words[i+2];
			else:
				nextWord = "";

		self.corpus = corpus;

	def generate(self, inputStr=False, debug=False):
		corpus = self.corpus;

		phrase = random.choice(list(corpus.keys()));
		output = phrase;

		if inputStr:
			parts = inputStr.split();

			if len(parts) >= 2:
				potential = parts[-2] + " " + parts[-1];
			else:
				potential = parts[-1];

			potentials = [];
			for key, value in corpus.items():
				if potential in key:
					potentials.append(key);

			if len(potentials) > 0:
				phrase = potentials[random.randint(0, len(potentials)-1)];
				output = inputStr;

		if not debug:
			while corpus[phrase] and len(corpus[phrase]) > 0 and len(output) < 1000:
				parts = phrase.split();

				nextWord = corpus[phrase][random.randint(0, len(corpus[phrase])-1)];

				output += (" " + nextWord)

				phrase = parts[1] + " " + nextWord;
		else:
			parts = inputStr.split();

			if len(parts) == 2:
				if inputStr not in corpus:
					output = "This phrase does not exist in the corpus.";
				else:
					available = ", ".join(corpus[inputStr]);

					if len(available) > 2048:
						available = len(corpus[inputStr]);
						output = "***" + inputStr + "*** has too many entries to list *(" + str(available) + ")*";
					else:
						output = "***" + inputStr + "*** **can end with the following *" + str(len(corpus[inputStr])) + "* words:** *";
						output += available;
						output += "*";
			else:
				output = "Invalid debug command, input *must* be 2 words in length.";

		return output.strip();

	def reload(self):
		self.corpus.clear();
		self.load();

	def __str__(self):
		return self.generate();

	def __int__(self):
		return len(self.corpus);

	def __len__(self):
		return len(self.corpus);

	def __getitem__(self, index):
		if index not in self.corpus:
			return None;

		return self.corpus[index];

	def __setitem__(self, index, value):
		self.corpus[index] = value;