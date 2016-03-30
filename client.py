import atexit;

import signal
import sys
def signal_handler(signal, frame):
	sys.exit(0);
signal.signal(signal.SIGINT, signal_handler);

import discord;
import asyncio;
client = discord.Client();

from markov import Corpus;
corpus = Corpus();

from phrases import getAPhrase;

from ping import PingPong;
ping = None;

from color import ColorPreview;

import getid;
# what the hell even is python
getid.client = client;

import json;

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

permittedChannels = [];
try:
	with open("permittedChannels.json", 'r', encoding="utf-8") as file:
		permittedChannels = json.load(file);
except FileNotFoundError:
	print("Permitted channel database doesn't exist, please use " + setting.CMD_START + " permit on a channel.");

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
			if message.channel.id in permittedChannels:
				await client.send_message(message.channel, str(cmds));
				return;
			else:
				return;

		if command.command == "permit":
			if message.author.name in setting.ELEVATED_USERS:
				if message.channel.id not in permittedChannels:
					permittedChannels.append(message.channel.id);
					with open('permittedChannels.json', 'w') as file:
						json.dump(permittedChannels, file);

					await client.send_message(message.channel, "Now permitted to use *" + message.channel.name + "*");

		# THIS RESIDES HERE TO ALLOW PERMIT AND NOTHING ELSE
		if message.channel.id not in permittedChannels:
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

		elif command.command == "phrase":
			if message.channel.is_private:
				print("Fetching phrase for " + message.author.name + " in a direct message")
			else:
				print("Fetching phrase for " + message.author.name + " in " + message.channel.name);

			tmp = await client.send_message(message.channel, '*Fetching phrase...*');

			await client.edit_message(tmp, getAPhrase());

		elif command.command == "ping":
			global ping;

			if not command.subcommand:
				ping = PingPong();

				await client.send_message(message.channel, setting.CMD_START + ' ping pong');
			elif command.subcommand == "pong" and message.author.id == client.user.id:
				ping.pong();
				print("Latency checked: " + str(int(ping)) + "ms");
				await client.edit_message(message, 'Pong!\nLatency: **' + str(int(ping)) + 'ms**');

		elif command.command == "color":
			if command.subcommand == "doc":
				await client.send_message(message.channel, "Please use the syntax used in **Pillow**:\nhttp://pillow.readthedocs.org/en/3.1.x/reference/ImageColor.html");
				return;

			if command.content:
				color = ColorPreview(command.content);

				try:
					await client.send_file(message.channel, color.stream, filename="color.png");
				except discord.Forbidden:
					await client.send_message(message.channel, "Cannot attach files in this channel.");

		elif command.command == "get":
			if command.subcommand == "userID":
				if not command.content:
					return;

				uid = getid.getUserID(getid.findUserByName(command.content, message.server));
				if uid:
					await client.send_message(message.channel, "User ID for *" + command.content + "* is **" + str(uid) + "**");
				else:
					await client.send_message(message.channel, "User could not be found.");

			if command.subcommand == "channelID":
				if not command.content:
					return;

				uid = getid.getChannelID(getid.findChannelByName(command.content, message.server));
				if uid:
					await client.send_message(message.channel, "Channel ID for *" + command.content + "* is **" + str(uid) + "**");
				else:
					await client.send_message(message.channel, "Channel could not be found.");

def close():
	client.logout();
atexit.register(close);

client.run(setting.EMAIL, setting.PASSWORD);
