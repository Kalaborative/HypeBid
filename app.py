from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from collections import Counter

app = Flask(__name__)

mongodbURI = 'mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test'

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/addbid', methods=["POST"])
def addbid():
	if request.method == "POST":
		newName = request.form["staticName"]
		newBid = request.form["bid"]
		print("Name: {}, Bid: {}".format(newName, newBid))
		with sqlite3.connect('bids.db') as connection:
			c = connection.cursor()
			c.execute('INSERT INTO bidData VALUES (?, ?)', (newName, newBid))
		return redirect(url_for("index"))

@app.route('/done')
def done():
	with sqlite3.connect('bids.db') as connection:
		c = connection.cursor()
		c.execute("SELECT * FROM bidData")
		allData = c.fetchall()
		dataDict = {}
		for a, b in allData:
			dataDict[a] = int(b)

		c = Counter(dataDict.values())
		winningBid = [item for item, count in Counter(c).items() if count == 1]
		print(winningBid)

		for a, b in dataDict.items():
			if b == min(winningBid):
				print("Winner is {}.".format(a))

		return redirect(url_for('index'))

@app.route("/getAll")
def getAll():
	with sqlite3.connect('bids.db') as connection:
		c = connection.cursor()
		c.execute("SELECT * FROM bidData")
		allData = c.fetchall()
		return render_template('results.html', data=allData)

if __name__ == "__main__":
	app.run(debug=True)