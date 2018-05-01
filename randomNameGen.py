from random import choice

def generate_bot():
	letters = "qwertyuiopasdfghjklzxcvbnm"
	numbers = "1234567890"
	store = []
	for i in range(5):
		store.append(choice(letters))
	for i in range(2):
		store.append(choice(numbers))
	identifier = "".join(store)
	return "bot_{}".format(identifier)