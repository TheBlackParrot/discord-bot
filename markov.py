import random;

import discord;
import asyncio;

import settings as setting;

client = discord.Client();

CORPUS_FILENAME = setting.CORPUS_FILENAME;
corpus = {};

def addToCorpus(line):
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


def generateMarkovChain(str):
	phrase = random.choice(list(corpus.keys()));
	output = phrase;

	if str:
		parts = str.split();

		if len(parts) >= 2:
			potential = parts[-2] + " " + parts[-1];
			if potential in corpus:
				phrase = potential;
				output = str;
		else:
			potentials = [];
			for key, value in corpus.items():
				if parts[0] in key:
					potentials.append(key);

			if len(potentials) > 0:
				phrase = potentials[random.randint(0, len(potentials)-1)];
				output = phrase;

	while corpus[phrase] and len(corpus[phrase]) > 0 and len(output) < 1000:
		parts = phrase.split();

		nextWord = corpus[phrase][random.randint(0, len(corpus[phrase])-1)];

		output += (" " + nextWord)

		phrase = parts[1] + " " + nextWord;

	return output.strip();


with open(CORPUS_FILENAME, 'r') as CORPUS_FILE:
	for line in CORPUS_FILE:
		if line:
			addToCorpus(line);
	#print(generateMarkovChain());

@client.event
async def on_ready():
	print('Logged in as');
	print(client.user.name);
	print(client.user.id);
	print('');
	invite = await client.accept_invite(setting.INVITE);
	print(invite);

@client.event
async def on_message(message):
	if message.content.startswith(setting.MARKOVCMD):
		tmp = await client.send_message(message.channel, 'Generating chain...');
		msgContent = message.content[len(setting.MARKOVCMD):].strip();
		await client.edit_message(tmp, generateMarkovChain(msgContent));
	
	if message.content.startswith(setting.MARKOVADDCMD):
		msgContent = message.content[len(setting.MARKOVADDCMD):].strip();

		addToCorpus(msgContent);
		
		with open(CORPUS_FILENAME, 'a') as CORPUS_FILE:
			CORPUS_FILE.write("\r\n" + msgContent);

		await client.send_message(message.channel, "Added '" + msgContent + "' to the corpus.");

client.run(setting.EMAIL, setting.PASSWORD);