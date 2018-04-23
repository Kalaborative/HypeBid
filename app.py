from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import sqlite3
from os import environ, urandom
from collections import Counter


mongodbURI = 'mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test'
postgresqlURI = 'postgres://whzqfjyetabwob:9790172026c6cb7d14db26d59ef338d7a2d172efa4c9d0bfd853e2cac22a0d34@ec2-174-129-41-64.compute-1.amazonaws.com:5432/dfo5pf6eevk67m'

app = Flask(__name__)
app.secret_key = urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = postgresqlURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create our database model
class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<User {}>'.format(self.username)

	def is_active(self):
		return True

	def get_id(self):
		return self.username

	def is_authenticated(self):
		return self.authenticated

	def is_anonymous(self):
		return False

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return User.query.filter_by(username=user_id).first()

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/register', methods=["POST"])
def register():
	if request.method == "POST":
		newName = request.form["username"]
		newPw = request.form["password"]
		user = User(newName, newPw)
		db.session.add(user)
		db.session.commit()
		login_user(user, remember=True)
		return redirect(url_for('index'))

@app.route('/logmein', methods=["POST"])
def logmein():
	if request.method == "POST":
		loginName = request.form["username"]
		loginPw = request.form["password"]
		user = User.query.filter_by(username=loginName).first()
		if user:
			user.authenticated = True
			db.session.add(user)
			db.session.commit()
			login_user(user, remember=True)
			return redirect(url_for('index'))
		else:
			return render_template('login.html', error_msg="Invalid credentials.")

@app.route('/logmeout')
@login_required
def logmeout():
	logout_user()
	return redirect(url_for('index'))


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

@app.route('/login')
def login():
	return render_template('login.html')

if __name__ == "__main__":
	app.run(debug=True)