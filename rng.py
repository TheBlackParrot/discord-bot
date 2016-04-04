from random import randint;
import json;

class EightBall():
	def __init__(self):
		try:
			with open("8ballResponses.json", "r", encoding="utf-8") as file:
				self.responses = json.load(file);
		except FileNotFoundError:
			print("Using default 8 ball responses.");
			
			self.responses = ["Yes", "No", "Maybe"];
			self.save();

	def save(self):
		try:
			with open("8ballResponses.json", "w", encoding="utf-8") as file:
				json.dump(self.responses, file);
		except:
			pass;

	def add(self, response):
		if response:
			self.responses.append(response);

		self.save();

	def remove(self, response):
		if response in self.responses:
			self.responses.remove(response);
			self.save();

			return True;
		else:
			return False;

	def __str__(self):
		return self.responses[randint(0, len(self.responses)-1)];
