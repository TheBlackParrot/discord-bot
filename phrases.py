import urllib.request;

import settings as setting;

def getAPhrase():
	req = urllib.request.Request(
		setting.PHRASES_URL,
		data=None,
		headers={
			'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.108 Safari/537.36'
		}
	);

	page = urllib.request.urlopen(req);
	return page.read().decode('utf-8');