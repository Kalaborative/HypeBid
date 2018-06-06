from pymongo import MongoClient
from collections import Counter

def listAllItems():
	"""Returns a list of all items."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	results = []
	for item in data.find():
		results.append(item['item_id'])
	return results

def addItem(newItemId, newItemName, newItemValue, newItemDesc, newItemMaxBid, newItemImage, newItemEndTime):
	"""Adds a new item with item ID starting with item_."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	newItemDict = {"item_id": int(newItemId), 'users_bidding': [], 'item_name': newItemName, 'item_value': newItemValue, 'item_desc': newItemDesc, "end_time": newItemEndTime, "max_bid": newItemMaxBid, 'item_img': newItemImage}
	data.insert_one(newItemDict)
	return True

def getValidItemIDs():
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	validItems = data.find()
	item_ids = []
	for item in validItems:
		item_ids.append(item['item_id'])
	return item_ids

def addBid(chosenItem, username, bid):
	"""Adds a bid to them item given its item ID, username, and bid amount."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	hist = client.hypeBidDB.userbids
	validgameIDs = getValidItemIDs()
	if chosenItem in validgameIDs:
		match = False
		biddingList = [i['users_bidding'] for i in data.find() if i['item_id'] == chosenItem][0]
		for b in biddingList:
			if b['user_name'] == username:
				match = True
		try:
			bid = float(bid)
			if match:
				print("Match was found, updating")
				data.update_one({'item_id': chosenItem, 'users_bidding.user_name': username}, {"$set": {'users_bidding.$.user_bid': bid}})
				hist.update_one({"username": username, 'history.game_id': chosenItem}, {"$push": {'history.$.bids': bid} })
				return True
			else:
				print("No match, checking if user has a history")
				newBidData = {"user_name": username, "user_bid": bid}
				data.update_one({'item_id': chosenItem}, {"$push": {"users_bidding": newBidData}})
				inHist = hist.find_one({"username": username})
				selectBid = {"game_id": chosenItem, 'bids': [bid]}
				if inHist:
					print("User has a history, updating")
					hist.update_one({"username": username}, {"$push": {"history": selectBid}})
				else:
					print("No history. Adding new entry")
					newHistEntry = {"username": username, "history": [selectBid]}
					hist.insert_one(newHistEntry)
				return True
		except:
			return False
	else:
		return False

def listItemBids():
	"""Returns a dict of all bids on each item."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	results = {}
	for d in data.find():
		results[d['item_id']] = d['users_bidding']
	return results

def clearAllBids():
	"""Removes all bids on all items."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	data.update_many({}, {"$set": {"users_bidding": []}})
	return True

def getBidHistory(username):
	"""Returns a dict of the username's bidding history by game."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	hist = client.hypeBidDB.userbids
	result = hist.find_one({"username": username})
	if result:
		gameHistory = result['history']
		return gameHistory
	else:
		return False


def calculate_winning_bid(chosenItem):
	"""Returns the user with the winning bid given a valid Item ID."""
	client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
	data = client.hypeBidDB.items
	validgameIDs = getValidItemIDs()
	if chosenItem in validgameIDs:
		biddingList = [i['users_bidding'] for i in data.find() if i['item_id'] == chosenItem][0]
		dataDict = {}
		for b in biddingList:
			dataDict[b['user_name']] = b['user_bid']

		c = Counter(dataDict.values())
		winningBid = [item for item, count in Counter(c).items() if count == 1]

		winresults = None

		for a, b in dataDict.items():
			if b == min(winningBid):
				winresults = "Winner is {}.".format(a)
		return winresults
	else:
		print("Item ID is not valid. Please try again.")
		return False