import random;
import time;
import json;
import collections;

class Slots():
	def __init__(self):
		self.slotsDB = {};
		try:
			with open('slotsdb.json', 'r', encoding="utf-8") as file:
				self.slotsDB = json.load(file);
		except FileNotFoundError:
			print("Slots database is currently a clean slate.");

		self.emotes = [
			":heart:",
			":smiley:",
			":poop:",
			":ok_hand:",
			":horse:",
			":earth_americas:",
			":moneybag:",
			":football:",
			":high_heel:",
			":rocket:",
			":100:",
			":ok:",
			":moyai:",
			":oncoming_automobile:",
			":eggplant:",
			":beer:",
			":japanese_goblin:"
		];

	def __getitem__(self, value):
		if not self.emotes[value]:
			return None;

		return self.emotes[value];

	def __len__(self):
		return len(self.emotes);

	def spin(self, userid, bet=50):
		if not userid:
			return;

		self.initUser(userid);

		self.slotsDB[userid]["tokens"] -= bet;

		output = {};
		output["values"] = [];
		output["userid"] = userid;

		for i in range(0, 3):
			output["values"].append(self[random.randint(0, len(self)-1)]);

		output["matches"] = collections.Counter(output["values"]);

		output["match_amount"] = 0;
		for key, val in output["matches"].items():
			if val > output["match_amount"]:
				output["match_amount"] = val;

		output["winnings"] = 0;
		if output["match_amount"] > 1:
			output["winnings"] = bet * (pow(output["match_amount"]-1, 3)) * 2;

		self.updateCooldown(userid);
		
		return output;

	def save(self, data):
		if not data:
			return;
		self.initUser(data["userid"]);

		savedata = self.slotsDB[data["userid"]];

		savedata["tokens"] += data["winnings"];

		self.slotsDB[data["userid"]] = savedata;

		try:
			with open('slotsdb.json', 'w', encoding="utf-8") as file:
				json.dump(self.slotsDB, file);
		except:
			print("Could not save slots database.");

	def updateCooldown(self, userid):
		if userid in self.slotsDB:
			self.slotsDB[userid]["cooldown"] = int(time.time());

	def getCooldown(self, userid):
		if userid not in self.slotsDB:
			return 0;

		return self.slotsDB[userid]["cooldown"];

	def initUser(self, userid):
		if userid not in self.slotsDB:
			self.slotsDB[userid] = {};
			self.slotsDB[userid]["cooldown"] = 0;
			self.slotsDB[userid]["tokens"] = 1000;

	def resetUser(self, userid):
		if userid not in self.slotsDB:
			self.initUser(userid);
		else:
			self.slotsDB[userid]["tokens"] = 1000;

	def getTokens(self, userid):
		if userid not in self.slotsDB:
			return 0;

		return self.slotsDB[userid]["tokens"];