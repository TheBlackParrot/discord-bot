import atexit;

import signal
import sys
def signal_handler(signal, frame):
	sys.exit(0);
signal.signal(signal.SIGINT, signal_handler)

import discord;
import asyncio;
client = discord.Client();

from markov import Corpus;
corpus = Corpus();

import settings as setting;
from settings import Commands;
cmds = Commands();

# e.g. to parse !tbp markov add
class CommandMessage():
	def __init__(self, data=None):
		self.data = data;

		words = data.split(" ");
		command = None;
		subcommand = None;
		content = None;

		if words[0]:
			if cmds.isCommand(words[0]):
				command = words[0];

		if len(words) >= 2:
			if cmds.isCommand(command, words[1]):
				subcommand = words[1];
				content = ' '.join(words[2:]);
			else:
				content = ' '.join(words[1:]);
		else:
			content = ' '.join(words[1:]);

		self.command = command;
		self.subcommand = subcommand;
		self.content = content;

	def command(self):
		return self.command;

	def subcommand(self):
		return self.subcommand;

	def content(self):
		return self.content;

@client.event
async def on_ready():
	print('Logged in as:');
	print(client.user.name);
	print(client.user.id);
	invite = await client.accept_invite(setting.INVITE);

@client.event
async def on_message(message):
	if message.content.startswith(setting.CMD_START):
		command = CommandMessage(message.content[len(setting.CMD_START):].strip());

		if not command.command:
			await client.send_message(message.channel, str(cmds));
			return;

		if command.command == "markov":
			if not command.subcommand:
				if message.channel.is_private:
					print("Generating chain for " + message.author.name + " in a direct message")
				else:
					print("Generating chain for " + message.author.name + " in " + message.channel.name);

				tmp = await client.send_message(message.channel, '*Generating chain...*');

				await client.edit_message(tmp, corpus.generate(command.content));

			elif command.subcommand == "add":
				content = command.content;

				print(message.author.name + " contributed " + '{:,}'.format(len(content)) + " bytes to the corpus");

				if content:
					content.replace("\r", "");
					contents = content.split("\n");

					for i in range(0, len(contents)):
						corpus.add(contents[i]);
					
					with open(corpus.filename, 'a') as file:
						file.write("\r\n" + content);

					await client.send_message(message.channel, "**Added** *'" + content + "'* **to the corpus.** \n\nReloading is not needed with this command.");

			elif command.subcommand == "reload":
				if message.author.name in setting.ELEVATED_USERS:
					print(message.author.name + " reloaded the corpus");

					old_size = corpus.filesize;
					corpus.reload();
					new_size = corpus.filesize;

					await client.send_message(message.channel, "Reloaded corpus.\nCorpus size changed by **" + str(round((new_size - old_size)/1024, 2)) + " KB**.\nCorpus is currently **" + str(round(new_size/1024, 2)) + " KB**");

			elif command.subcommand == "stats":
				msgContent = "Corpus size: **" + str(round((corpus.filesize)/1024, 2)) + " KB**";
				msgContent += "\nCorpus entries: **" + '{:,}'.format(len(corpus)) + "**";

				await client.send_message(message.channel, msgContent);

	'''
	if message.content.startswith(setting.MARKOVDEBUGCMD):
		if message.author.name in setting.ELEVATED_USERS:
			msgParts = message.content.split();

			if len(msgParts) > 1:
				if msgParts[1] == "canEnd":
					tmp = await client.send_message(message.channel, 'Generating debug message...');
					msgContent = message.content[len(setting.MARKOVDEBUGCMD + " canEnd"):].strip();
					await client.edit_message(tmp, corpus.generate(msgContent, 1));
	'''

def close():
	client.logout();
atexit.register(close);

client.run(setting.EMAIL, setting.PASSWORD);
