import sqlite3

with sqlite3.connect("bids.db") as connection:
	c = connection.cursor()
	c.execute("CREATE TABLE IF NOT EXISTS bidData (name TEXT, amount TEXT)")

