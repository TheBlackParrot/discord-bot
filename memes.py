import urllib.request;
import json;
from collections import OrderedDict;

class Memes():
	def __init__(self, user_agent="Mozilla/5.0 (X11; Linux x86_64)"):
		req = urllib.request.Request(
			"http://memegen.link/aliases/",
			data=None,
			headers={
				'User-Agent': user_agent
			}
		);

		data = json.loads(urllib.request.urlopen(req).read().decode('utf-8'));
		to_sort = {};

		for key, value in data.items():
			if len(data[key]["styles"]) > 0:
				for style in data[key]["styles"]:
					str = data[key]["template"].replace("templates/", "", 1) + "/::INPUT::.jpg?alt=" + style;
					new_key = key + "-" + style;

					if new_key not in to_sort:
						to_sort[new_key] = str;
			else:
				if key not in to_sort:
					to_sort[key] = data[key]["template"].replace("templates/", "", 1) + "/::INPUT::.jpg";

		self.data = OrderedDict(sorted(to_sort.items()));

	def __len__(self):
		return len(self.data);

	def items(self):
		return self.data.items();

	def keys(self):
		return self.data.keys();

	def __getitem__(self, value):
		if value in self.data:
			return self.data[value];

		return None;

	def normalize_input(self, data):
		data = str(data);

		data = data.replace("-", "--");
		data = data.replace("_", "__");
		data = data.replace(" ", "-");
		data = data.replace("?", "~q");
		data = data.replace("%", "~p");
		data = data.replace("\"", "''");

		return data;

	def generate(self, template, top_line="YOUR TEXT", bottom_line=None):
		if template not in self.data:
			return None;

		if len(top_line) <= 0:
			return None;
		
		top_line = self.normalize_input(top_line);
		if bottom_line:
			bottom_line = self.normalize_input(bottom_line);

		if bottom_line:
			url = self.data[template].replace("::INPUT::", "/".join([top_line, bottom_line]), 1);
		else:
			url = self.data[template].replace("::INPUT::", top_line, 1);

		return url;