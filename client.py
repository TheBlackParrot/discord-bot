import atexit;
import signal;
import sys;
import discord;
import asyncio;
from markov import Corpus;
from phrases import getAPhrase;
from ping import PingPong;
from color import ColorPreview;
import getid;
import json;
import time;
from slots import Slots;
import settings as setting;
from settings import Commands;
from ctypes.util import find_library;
# from audio import VoiceQueue, VoiceSystem;
from rng import EightBall;

def signal_handler(signal, frame):
	sys.exit(0);
signal.signal(signal.SIGINT, signal_handler);

client = discord.Client();

corpus = Corpus();

ping = None;

slots = Slots();

cmds = Commands();

# what the hell even is python
getid.client = client;

if not discord.opus.is_loaded():
	discord.opus.load_opus(find_library("opus"));

VoiceObj = None;
VoiceObjPlayer = None;
VoiceSubmitter = None;

eightBall = EightBall();

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
	print('Logged in!');
	print('----------');

	print(client.user.name);
	print(client.user.id);

	print('----------');
	for i in range(0, len(setting.INVITES)):
		try:
			await client.accept_invite(setting.INVITES[i]);
		except discord.errors.NotFound:
			print("Invite " + setting.INVITES[i] + " has expired.");

	if len(setting.INVITES) > 0:
		print('----------');

@client.event
async def on_message(message):
	if message.content.startswith(setting.CMD_START):
		command = CommandMessage(message.content[len(setting.CMD_START):].strip());

		if not message.channel.is_private:
			if not command.command:
				if message.channel.id in permittedChannels:
					await client.send_message(message.channel, str(cmds));
					return;
				else:
					return;

			if command.command == "permit":
				if message.author.name in setting.ELEVATED_USERS:
					if not command.subcommand:
						if message.channel.id not in permittedChannels:
							permittedChannels.append(message.channel.id);
							with open('permittedChannels.json', 'w') as file:
								json.dump(permittedChannels, file);

							print("Can now respond in channel ID " + str(message.channel.id));
							await client.send_message(message.channel, "Now permitted to use *" + message.channel.name + "*");
					elif command.subcommand == "remove":
						if message.channel.id in permittedChannels:
							permittedChannels.remove(message.channel.id);
							with open('permittedChannels.json', 'w') as file:
								json.dump(permittedChannels, file);

							print("Can no longer respond in channel ID " + str(message.channel.id));
							await client.send_message(message.channel, "No longer permitted to use *" + message.channel.name + "*");

			# THIS RESIDES HERE TO ALLOW PERMIT AND NOTHING ELSE
			if message.channel.id not in permittedChannels:
				return;
		else:
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

		elif command.command == "slots":
			mention = "";
			if not message.channel.is_private:
				mention = message.author.mention + "\n";

			slots.initUser(message.author.id);

			if command.subcommand == "spin":
				if int(time.time()) < slots.getCooldown(message.author.id) + 15:
					return;

				if not command.content:
					bet = 50;
				else:
					try:
						bet = int(command.content);
					except ValueError:
						await client.send_message(message.channel, mention + "Invalid bet amount, not a number.");
						return;

				if bet < 50:
					await client.send_message(message.channel, mention + "Invalid bet amount, bet must be higher than 50");
					return;

				if bet > slots.getTokens(message.author.id):
					await client.send_message(message.channel, mention + "Invalid bet amount, bet must be lower than " + str(slots.getTokens(message.author.id)));
					return;

				output = slots.spin(message.author.id, bet=bet);

				msgContent = "You are betting **" + str(bet) + " tokens**\n\n";
				msgContent += ' '.join(output["values"]) + "\n\n";
				if output["match_amount"] > 1:
					msgContent += "You won **" + str(output["winnings"]) + " tokens!**";
				else:
					msgContent += "You did not win anything. :frowning:";

				# i'd think python would update this in time, but apparently not
				msgContent += "\nYou now have **" + str(slots.getTokens(message.author.id) + output["winnings"]) + " tokens**";

				await client.send_message(message.channel, mention + msgContent);

				slots.save(output);

			if command.subcommand == "reset":
				slots.resetUser(message.author.id);
				await client.send_message(message.channel, mention + "Your tokens have been reset.");

			if command.subcommand == "tokens":
				await client.send_message(message.channel, mention + "You have **" + str(slots.getTokens(message.author.id)) + " tokens**.");

		elif command.command == "audio":
			global VoiceObj;
			global VoiceObjPlayer;
			global VoiceSubmitter;

			if command.subcommand == "join":
				if not command.content:
					return;

				if message.author.name not in setting.ELEVATED_USERS:
					return;

				channel = getid.findChannelByName(command.content, message.server);
				if not channel:
					await client.send_message(message.channel, "Channel does not exist");
					return;

				if str(channel.type) != "voice":
					await client.send_message(message.channel, "Channel is not a voice channel");
					return;

				if VoiceObj:
					if VoiceObj.is_connected():
						await VoiceObj.disconnect();

				VoiceObj = await client.join_voice_channel(channel);

			if command.subcommand == "play":
				if not command.content:
					return;

				if not VoiceObj:
					return;

				if not VoiceObj.is_connected():
					return;

				if message.server.id != VoiceObj.channel.server.id:
					return;

				if VoiceObjPlayer:
					if VoiceObjPlayer.is_playing():
						try:
							await client.delete_message(message);
						except:
							pass;

						await client.send_message(message.channel, "Currently playing audio, please wait for it to finish.");
						return;

				# create_ffmpeg_player doesn't seem very fleshed out at the moment?
				VoiceObjPlayer = await VoiceObj.create_ytdl_player(command.content);
				VoiceObjPlayer.start();

				VoiceSubmitter = message.author.id;

				try:
					await client.delete_message(message);
				except:
					pass;

				msgContent = "Playing **" + VoiceObjPlayer.title + "**";
				
				msgContent += "\n\n**Uploader:** " + VoiceObjPlayer.uploader;

				msgContent += "\n**Submitter:** " + message.author.mention;

				m, s = divmod(VoiceObjPlayer.duration, 60);
				h, m = divmod(m, 60);
				msgContent += "\n**Duration:** " + ("%d:%02d:%02d" % (h, m, s));

				msgContent += "\n**Views:** " + "{:,}".format(VoiceObjPlayer.views);

				percentage = (VoiceObjPlayer.likes / (VoiceObjPlayer.likes + VoiceObjPlayer.dislikes)) * 100;
				msgContent += "\n**Likes/Dislikes:** " + "{:,}".format(VoiceObjPlayer.likes) + " : " + "{:,}".format(VoiceObjPlayer.dislikes) + "*(" + str(round(percentage, 1)) + "% like this)*";
				
				await client.send_message(message.channel, msgContent);

			if command.subcommand == "stop":
				if not VoiceObj:
					return;

				if not VoiceObj.is_connected():
					return;

				if message.server.id != VoiceObj.channel.server.id:
					return;

				if VoiceObjPlayer:
					if VoiceObjPlayer.is_playing():
						if VoiceSubmitter == message.author.id or message.author.name in setting.ELEVATED_USERS:
							await VoiceObjPlayer.stop();

			if command.subcommand == "leave":
				if not VoiceObj:
					return;

				if not VoiceObj.is_connected():
					return;

				if message.server.id != VoiceObj.channel.server.id:
					return;

				await VoiceObj.disconnect();

		elif command.command == "8ball":
			if not command.subcommand:
				response = str(eightBall);
				mention = (message.author.mention + " ") if not message.channel.is_private else "";

				await client.send_message(message.channel, mention + ":crystal_ball: **" + response + "** :crystal_ball:");
			
			elif command.subcommand == "add":
				if not command.content:
					return;

				if message.author.name not in setting.ELEVATED_USERS:
					return;

				eightBall.add(command.content);
				await client.send_message(message.channel, "Added *" + command.content + "* as an 8 ball response.");

			elif command.subcommand == "remove":
				if not command.content:
					return;

				if message.author.name not in setting.ELEVATED_USERS:
					return;

				if eightBall.remove(command.content):
					await client.send_message(message.channel, "Removed *" + command.content + "* from the 8 ball responses.");
				else:
					await client.send_message(message.channel, "*" + command.content + "* is not an 8 ball response.");

		elif command.command == "avatar":
			if not message.mentions or message.channel.is_private:
				if message.author.avatar_url:
					await client.send_message(message.channel, message.author.avatar_url);
			else:
				output = "";
				for i in range(0, len(message.mentions)):
					output += message.mentions[i].avatar_url + "\n";

				await client.send_message(message.channel, output);


def close():
	client.logout();
atexit.register(close);

client.run(setting.EMAIL, setting.PASSWORD);
