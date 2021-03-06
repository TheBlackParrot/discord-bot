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
from audio import VoiceSettings, getYTDLInfo;
from rng import EightBall;
from memes import Memes;
import math;

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
vset = VoiceSettings();

eightBall = EightBall();

memes = Memes();

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
		if message.channel.is_private and setting.DISABLE_DM:
			return;
			
		command = CommandMessage(message.content[len(setting.CMD_START):].strip());

		default_output = str(cmds);
		default_output += "\n\n:pencil: **Syntax:** " + setting.CMD_START + " [command] *[subcommand] [content]*";

		if not message.channel.is_private:
			tmp = [];

			for i in range(0, len(setting.ELEVATED_USERS)):
				username = setting.ELEVATED_USERS[i];

				if getid.findUserByName(username, message.server):
					tmp.append(username);

			if len(tmp) > 0:
				default_output += "\n\n:white_check_mark: **Elevated Users:** " + ', '.join(tmp);

		default_output += "\n\nhttps://github.com/TheBlackParrot/discord-bot";

		if not message.channel.is_private:
			if not command.command:
				if message.channel.id in permittedChannels:
					await client.send_message(message.channel, default_output);
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
				await client.send_message(message.channel, default_output);
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

			global VoiceSettings;

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

			elif command.subcommand == "play":
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

				# TODO: normalize this crap
				linkInfo = getYTDLInfo(command.content);
				url = None;
				codec = None;

				if "format" not in linkInfo:
					if "url" in linkInfo["info"]:
						url = linkInfo["info"]["url"];

						if "acodec" in linkInfo["info"]:
							codec = linkInfo["info"]["acodec"];
						elif "ext" in linkInfo["info"]:
							codec = linkInfo["info"]["ext"];

					else:
						await client.send_message(message.channel, "No stream URL could be found, probably an unsupported service.");
						return;		
				else:
					if "url" in linkInfo["format"]:
						url = linkInfo["format"]["url"];

						if "acodec" in linkInfo["format"]:
							codec = linkInfo["format"]["acodec"];
						elif "ext" in linkInfo["format"]:
							codec = linkInfo["format"]["ext"];

					else:
						await client.send_message(message.channel, "No stream URL could be found, probably an unsupported service.");
						return;				

				if not url or not codec:
					return;

				if codec == "opus":
					vset.update("rate", 48000);
				else:
					vset.update("rate", 44100);

				VoiceObjPlayer = VoiceObj.create_ffmpeg_player(url, options=str(vset));
				VoiceObjPlayer.start();

				VoiceSubmitter = message.author.id;

				try:
					await client.delete_message(message);
				except:
					pass;

				msgContent = "Playing **" + linkInfo["info"]["title"] + "**";
				
				if "uploader" in linkInfo["info"]:
					msgContent += "\n\n**Uploader:** " + linkInfo["info"]["uploader"];

				msgContent += "\n**Submitter:** " + message.author.mention;

				if "duration" in linkInfo["info"]:
					m, s = divmod(linkInfo["info"]["duration"], 60);
					h, m = divmod(m, 60);
					msgContent += "\n**Duration:** " + ("%d:%02d:%02d" % (h, m, s));

					if vset.tempo != 1:
						m, s = divmod(math.ceil(linkInfo["info"]["duration"]/vset.tempo), 60);
						h, m = divmod(m, 60);
						msgContent += " *(adjusted: " + ("%d:%02d:%02d" % (h, m, s)) + ")*";

				if "view_count" in linkInfo["info"]:
					msgContent += "\n**Views:** " + "{:,}".format(linkInfo["info"]["view_count"]);

				if "like_count" in linkInfo["info"]:
					if "dislike_count" in linkInfo["info"]:
						percentage = (linkInfo["info"]["like_count"] / (linkInfo["info"]["like_count"] + linkInfo["info"]["dislike_count"])) * 100;
						msgContent += "\n**Likes/Dislikes:** " + "{:,}".format(linkInfo["info"]["like_count"]) + " : " + "{:,}".format(linkInfo["info"]["dislike_count"]) + "*(" + str(round(percentage, 1)) + "% like this)*";
					else:
						msgContent += "\n**Likes:** " + "{:,}".format(linkInfo["info"]["like_count"]);
				
				await client.send_message(message.channel, msgContent);

			elif command.subcommand == "stop":
				if not VoiceObj:
					return;

				if not VoiceObj.is_connected():
					return;

				if message.server.id != VoiceObj.channel.server.id:
					return;

				if VoiceObjPlayer:
					if VoiceObjPlayer.is_playing():
						if VoiceSubmitter == message.author.id or message.author.name in setting.ELEVATED_USERS:
							VoiceObjPlayer.stop();

			elif command.subcommand == "leave":
				if not VoiceObj:
					return;

				if not VoiceObj.is_connected():
					return;

				if message.server.id != VoiceObj.channel.server.id:
					return;

				await VoiceObj.disconnect();

			elif command.subcommand == "setting":
				if message.author.name not in setting.ELEVATED_USERS:
					return;

				add = "";
				if VoiceObjPlayer:
					if VoiceObjPlayer.is_playing():
						add = "\n\nSettings will not be applied until the audio is restarted.";

				if not command.content:
					await client.send_message(message.channel, "**Available settings:**\n*volume, pitch, tempo*" + add);
					return;

				if command.content:
					parts = command.content.split(" ");

					if len(parts) < 2:
						return;

					set = parts[0];
					value = float(parts[1]);

					new = vset.update(set, value);

					if new:
						await client.send_message(message.channel, "Updated *" + set + "* to *" + str(new) + "*" + add);

			elif command.subcommand == "debug":
				if message.author.name not in setting.ELEVATED_USERS:
					return;

				output = [];

				if VoiceObj:
					output.append("in voice channel `" + VoiceObj.channel.name + "`");
					if VoiceObjPlayer:
						if VoiceObjPlayer.is_playing():
							output.append("**Status**: playing");
						else:
							output.append("**Status**: not playing");
					else:
						output.append("**Status**: not playing");
				else:
					output.append("not in voice channel");

				output.append("**Filters:** `" + str(vset) + "`");
				output.append("**Settings:** volume = " + str(vset.volume) + ", pitch = " + str(vset.pitch) + ", tempo = " + str(vset.tempo));

				if vset.tempo / vset.pitch < 0.5 or vset.tempo / vset.pitch > 2:
					output.append(":warning: filter `atempo` is outside the required range of `0.5 - 2`");

				await client.send_message(message.channel, "\n".join(output));


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
			output = [];

			if message.channel.is_private or not command.content:
				if message.author.avatar_url:
					output.append(message.author.avatar_url);
			else:
				if message.mentions:
					for i in range(0, len(message.mentions)):
						output.append(message.mentions[i].avatar_url);

				else:
					names = message.content.split(" ");
					for i in range(0, len(names)):
						name = names[i];
						user = getid.findUserByName(name, message.server);

						if user:
							if user.avatar_url:
								output.append(user.avatar_url);

			if len(output) > 0:
				await client.send_message(message.channel, "\n".join(output).strip());

		elif command.command == "meme":
			if not command.subcommand and command.content:
				template = command.content.split(" ", maxsplit=1)[0];
				if template not in memes.data:
					return;

				inputs = command.content.split("line:");

				lines = [];
				for i in range(1, len(inputs)):
					if len(lines) >= 2:
						break;

					line = inputs[i].strip();
					if line:
						lines.append(line);

				if not len(lines):
					return;
				elif len(lines) == 1:
					output = memes.generate(template, top_line=lines[0]);
				elif len(lines) == 2:
					output = memes.generate(template, top_line=lines[0], bottom_line=lines[1]);

				await client.send_message(message.channel, output);

			elif command.subcommand == "list":
				if not command.content:
					await client.send_message(message.channel, "Please enter a letter/number to list templates, all templates cannot be listed at once.");
					return;

				char = command.content[0].lower();

				output = [];
				for key in memes.keys():
					if key[0] == char:
						output.append(key);

				if len(output):
					await client.send_message(message.channel, "**The following templates are available:**\n*" + ", ".join(output) + "*");

def close():
	client.logout();
atexit.register(close);

while True:
	if not client.is_logged_in:
		try:
			client.run(setting.EMAIL, setting.PASSWORD);
		except:
			pass;

	time.sleep(10);
