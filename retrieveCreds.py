import requests

def getCredentials():
	url = 'https://pastebin.com/raw/8VwDb2Bp'
	r = requests.get(url).text
	keys = str(r).splitlines()
	reduceKeys = [k.split(" = ") for k in keys]
	# print(reduceKeys)

	credDict = {}
	for r in reduceKeys:
		credDict[r[0]] = r[1]

	return credDict
