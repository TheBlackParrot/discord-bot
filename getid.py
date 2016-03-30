def findUserByName(name, server):
	members = client.get_all_members();

	for member in members:
		if member.server == server:
			if member.name == name:
				return member;

	return None;

def findChannelByName(name, server):
	channels = client.get_all_channels();

	for channel in channels:
		if channel.server == server:
			if channel.name == name:
				return channel;

	return None;


def getUserID(user):
	if not user:
		return None;
	if not user.id:
		return None;

	return user.id;

def getChannelID(channel):
	if not channel:
		return None;
	if not channel.id:
		return None;

	return channel.id;