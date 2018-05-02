from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
# from flask_wtf import FlaskForm
import re
from datetime import datetime
from randomNameGen import generate_bot
# from wtforms import Form, BooleanField, StringField, validators, SubmitField, PasswordField
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import sqlite3
from os import environ, urandom
from collections import Counter


mongodbURI = 'mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test'
postgresqlURI = 'postgres://whzqfjyetabwob:9790172026c6cb7d14db26d59ef338d7a2d172efa4c9d0bfd853e2cac22a0d34@ec2-174-129-41-64.compute-1.amazonaws.com:5432/dfo5pf6eevk67m'
# Heroku CLI PG PSQL Command: heroku pg:psql postgresql-curly-40771 --app hypebids-dev


app = Flask(__name__)
app.secret_key = urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = postgresqlURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

# class RegistrationForm(FlaskForm):
# 	username = StringField('Username', [validators.Length(min=4, max=25)])
# 	email = StringField('Email Address', [validators.Length(min=6, max=35)])
# 	initialPw = PasswordField('Set password')
# 	confirmPw = PasswordField('Confirm Password', [validators.EqualTo('initialPw', message="Passwords did not match.")])
# 	accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
# 	submit = SubmitField("Send")

# @app.route('/testregister')
# def testregister():
# 	form = RegistrationForm()
# 	return render_template("testlog.html", form=form)


# Create our database model
class User(db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(120), unique=True)
	password = db.Column(db.String(120))
	email = db.Column(db.String(150), unique=True)
	creation_date = db.Column(db.String(50))
	isdummy = db.Column(db.Boolean())
	isadmin = db.Column(db.Boolean())

	def __init__(self, username, password, email, creation_date, isdummy, isadmin):
		self.username = username
		self.password = password
		self.email = email
		self.creation_date = creation_date
		self.isdummy = isdummy
		self.isadmin = isadmin

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
	return render_template('app.html')

@app.route('/admin/<username>')
@login_required
def admin(username):
	if current_user.isadmin:
		return render_template('admin.html')
	else:
		return "Sorry, you don't have permission to view this page."

@app.route("/admin/<username>/botmanage")
@login_required
def manage_bot(username):
	if current_user.isadmin:
		return render_template('manage_bot.html')
	else:
		return abort(403)

@app.route('/.well-known/acme-challenge/0loVw881ncAco8Q9IwVtWrTeEDqopXQAE6W2Ag9CS58')
def static_file():
	return app.send_static_file('0loVw881ncAco8Q9IwVtWrTeEDqopXQAE6W2Ag9CS58')

@app.route('/makebot', methods=["POST"])
def makebot():
	if request.method == "POST":
		botName = generate_bot()
		botPw = botName[4:]
		botEmail = "{}@testbot.com".format(botName)
		botCreation = datetime.today().strftime("%x %X %p")
		bot = User(botName, botPw, botEmail, botCreation, True, False)
		db.session.add(bot)
		db.session.commit()
		return jsonify({"status": "OK"})

@app.route('/checkbots', methods=["POST"])
def checkbots():
	if request.method == "POST":
		botList = []
		dummies = User.query.filter(User.isdummy==True)
		for d in dummies:
			botList.append(d)
		return jsonify({"number": len(botList)})

@app.route('/deletebot', methods=["POST"])
def deletebot():
	if request.method == "POST":
		dummies = User.query.filter(User.isdummy==True)
		for d in dummies:
			db.session.delete(d)
			db.session.commit()
		return jsonify({"status": "OK"})		


@app.route('/register', methods=["POST"])
def register():
	if request.method == "POST":
		newName = request.form["registerUname"]
		if len(newName) < 5:
			# return render_template('login.html', error_msg="Username cannot be less than five characters.")
			return jsonify({"error": "Username cannot be less than five characters."})
		registeredUsers = User.query.all()
		regUsernames = []
		for r in registeredUsers:
			regUsernames.append(r.username)
		if newName in regUsernames:
			return jsonify({"error": "This username is already taken. Sign in or use another one."})
		newPw = request.form["registerPw"]
		confirmPw = request.form["confirmPw"]
		if newPw != confirmPw:
			# return render_template('login.html', error_msg="Passwords must match.")
			return jsonify({"error": "Passwords must match."})
		registerEmail = request.form["email"]
		if not EMAIL_REGEX.match(registerEmail):
			# return render_template('login.html', error_msg="Please enter a valid email address.")
			return jsonify({"error": "Please enter a valid email address."})
		try:
			terms = request.form["agree"]
		except:
			return jsonify({"error": "You must accept our terms and conditions to register."})
		registerDate = datetime.today().strftime("%x %X %p")
		user = User(newName, newPw, registerEmail, registerDate, False, False)
		db.session.add(user)
		db.session.commit()
		# return redirect(url_for('login', success_msg="Account creation success!"))
		# return render_template('login.html', success_msg="Account creation successful!")
		return jsonify({"message": "Account creation successful! Please sign in."})

@app.route('/logmein', methods=["POST"])
def logmein():
	if request.method == "POST":
		loginName = request.form["loginUname"]
		loginPw = request.form["loginPw"]
		if len(loginName) < 5:
			# return render_template('login.html', error_msg="Username cannot be less than five characters.")
			return jsonify({"error": "Username cannot be less than five characters."})
		user = User.query.filter_by(username=loginName).first()
		if user:
			if user.password == loginPw:	
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=True)
				return redirect(url_for('index'))
			else:
				# return render_template('login.html', error_msg="Wrong password.")
				return jsonify({"error": "Wrong password."})
		else:
			# return render_template('login.html', error_msg="Invalid credentials.")
			return jsonify({"error": "Invalid username."})

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

@app.route('/admin/<username>/allusers')
@login_required
def allUsers(username):
	if current_user.isadmin:
		dbUsers = User.query.all()
		return render_template('manage_users.html', accounts=dbUsers)
	else:
		abort(403)

@app.route('/login')
def login():
	return render_template('login.html')

if __name__ == "__main__":
	# convention to run on Heroku
	port = int(environ.get("PORT", 5000))
	# run the app available anywhere on the network, on debug mode
	app.run(host="0.0.0.0", port=port, debug=True)
	# app.run(debug=True)