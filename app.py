from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
# from flask_wtf import FlaskForm
import re
from datetime import datetime
from randomNameGen import generate_bot
# from wtforms import Form, BooleanField, StringField, validators, SubmitField, PasswordField
from flask_sqlalchemy import SQLAlchemy
from random import choice, uniform
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
import sqlite3
from flask_uploads import UploadSet, configure_uploads, IMAGES
from bidfuncs import getValidItemIDs, addItem, addBid, listItemBids, calculate_winning_bid, clearAllBids, getBidHistory
from pymongo import MongoClient
from maxbidcalc import determine_max_bid
from s3 import uploadToS3
from os import environ, urandom
from collections import Counter


mongodbURI = 'mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test'
postgresqlURI = 'postgres://whzqfjyetabwob:9790172026c6cb7d14db26d59ef338d7a2d172efa4c9d0bfd853e2cac22a0d34@ec2-174-129-41-64.compute-1.amazonaws.com:5432/dfo5pf6eevk67m'
# Heroku CLI PG PSQL Command: heroku pg:psql postgresql-curly-40771 --app hypebids-dev

# Pymongo Shell Commands:
# client = MongoClient("mongodb+srv://HBDB_User:DTfjUidPbZfAhdlF@hypebiddb-xkxgt.mongodb.net/test")
# data = client.hypeBidDB.items

FILE_UPLOAD_TEMP_DIR = "itemUploads"


app = Flask(__name__)
photos = UploadSet('photos', IMAGES)
app.secret_key = urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = postgresqlURI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOADED_PHOTOS_DEST'] = FILE_UPLOAD_TEMP_DIR
db = SQLAlchemy(app)
EMAIL_REGEX = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
configure_uploads(app, photos)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# class RegistrationForm(FlaskForm):
# 	username = StringField('Username', [validators.Length(min=4, max=25)])
# 	email = StringField('Email Address', [validators.Length(min=6, max=35)])
# 	initialPw = PasswordField('Set password')
# 	confirmPw = PasswordField('Confirm Password', [validators.EqualTo('initialPw', message="Passwords did not match.")])
# 	accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])
# 	submit = SubmitField("Send")


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

def userIsValid(name):
	registeredUsers = User.query.all()
	regUsernames = []
	for r in registeredUsers:
		regUsernames.append(r.username.lower())
	return name.lower() in regUsernames

@app.route('/')
def index():
	gameIDs = getValidItemIDs()
	return render_template('homepage.html', allgames=gameIDs)

@app.route('/games')
@login_required
def games():
	client = MongoClient(mongodbURI)
	data = client.hypeBidDB.items
	gameInfo = []
	for d in data.find():
		gameInfo.append([d['item_name'], len(d['users_bidding']), d['item_id']])
	return render_template('gamelist.html', games=gameInfo)

@app.route("/game/<int:game_id>")
@login_required
def game(game_id):
	gameIDs = getValidItemIDs()
	if game_id in gameIDs:
		client = MongoClient(mongodbURI)
		data = client.hypeBidDB.items
		results = data.find_one({'item_id': game_id})
		return render_template("detail.html", gameid=results['item_id'], ItemName=results['item_name'], ItemDesc=results['item_desc'], 
			ItemValue=results['item_value'], ItemMaxBid=results['max_bid'], ItemImage=results['item_img'], ItemEndTime=results['end_time'])
	else:
		return abort(404)

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

@app.route("/addnewitem", methods=["POST"])
def addnewitem():
	if request.method == "POST":
		nItemName = request.form["itemName"]
		nItemDesc = request.form["itemDesc"]
		nItemVal = request.form["itemValue"]
		nImage = photos.save(request.files['itemImg'])
		nImageUrl = uploadToS3(nImage)
		nItemEndDate = request.form['itemdatetime']
		nums = [0,1,2,3,4,5,6,7,8,9]
		chosenNums = []
		for i in range(9):
			n = choice(nums)
			chosenNums.append(str(n))
		uniqueID = "".join(chosenNums)
		nItemMaxBid = determine_max_bid(nItemVal)
		res = addItem(uniqueID, nItemName, nItemVal, nItemDesc, nItemMaxBid, nImageUrl, nItemEndDate)
		if res:
			return render_template("newitemform.html", statusmsg=uniqueID)
		else:
			return "Failed to make a new item."

@app.route("/submitBid", methods=["POST"])
def submitBid():
	if request.method == "POST":
		uname = current_user.username
		current_game = int(request.json['game'])
		ubid = round(float(request.json['bid']), 2)
		addBid(current_game, uname, ubid)
		return jsonify({"status": "OK"})

@app.route('/register', methods=["POST"])
def register():
	if request.method == "POST":
		newName = request.form["registerUname"]
		if len(newName) < 5:
			# return render_template('login.html', error_msg="Username cannot be less than five characters.")
			return jsonify({"error": "Username cannot be less than five characters."})
		if userIsValid(newName.lower()):
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
		regEmails = []
		for r in User.query.all():
			regEmails.append(r.email.lower())
		if registerEmail.lower() in regEmails:
			return jsonify({"error": "This email is already being used. Please sign in."})
		try:
			terms = request.form["agree"]
		except:
			return jsonify({"error": "You must accept our terms and conditions to register."})
		registerDate = datetime.today().strftime("%x %X %p")
		newName = newName.lower()
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
		loginName = loginName.lower()
		user = User.query.filter_by(username=loginName).first()
		if user:
			if user.password == loginPw:	
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=True)
				return jsonify({"status": "OK"})
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

@app.route('/admin/<username>/allusers')
@login_required
def allUsers(username):
	if current_user.isadmin:
		dbUsers = User.query.all()
		return render_template('manage_users.html', accounts=dbUsers)
	else:
		abort(403)

@app.route('/admin/<username>/makenewitem')
@login_required
def makeNewItem(username):
	if current_user.isadmin:
		return render_template("newitemform.html", statusmsg=None)
	else:
		abort(403)

@app.route('/user/<username>')
@login_required
def profile(username):
	if userIsValid(username):
		userBidHistory = getBidHistory(username.lower())
		return render_template('profile.html', history=userBidHistory)

@app.route("/admin/<username>/simulatebidding")
@login_required
def simulateBidding(username):
	if current_user.isadmin:
		gameIDs = getValidItemIDs()
		bids = listItemBids()
		return render_template("simbids.html", allgames=gameIDs, bids=bids)
	else:
		abort(403)

@app.route('/signup')
def testRegister():
	return render_template('register.html')

@app.route("/runsimulation", methods=["POST"])
def runSimulation():
	if request.method == "POST":
		allDummies = User.query.filter(User.isdummy == True)
		if allDummies.first():
			botlist = []
			for dummy in allDummies:
				botlist.append(dummy.username)
			formGameID = int(request.json['game'])
			client = MongoClient(mongodbURI)
			data = client.hypeBidDB.items
			maxBid = data.find_one({"item_id": formGameID})['max_bid']
			maxBidFloat = float(maxBid)
			for b in botlist:
				randBid = round(uniform(0.01, maxBidFloat), 2)
				addBid(formGameID, b, randBid)
			return jsonify({"success": "Simulation complete!", "error": False})
		else:
			return jsonify({"success": False, "error": "No dummy accounts located."})

@app.route("/calculatewinner", methods=["POST"])
def calculateWinner():
	if request.method == "POST":
		formGameID = int(request.json['game'])
		winner = calculate_winning_bid(formGameID)
		return jsonify({"status": winner})

@app.route("/clearbids", methods=["POST"])
def clearBids():
	if request.method == "POST":
		clearAllBids()
		return jsonify({"status": "OK"})

@app.route('/deletegame', methods=["POST"])
def deleteGame():
	if request.method == "POST":
		formGameID = int(request.json['game'])
		client = MongoClient(mongodbURI)
		data = client.hypeBidDB.items
		data.delete_one({"item_id": formGameID})
		return jsonify({"status": "OK"})

@app.route('/login')
def login():
	return render_template('login.html')

if __name__ == "__main__":
	# convention to run on Heroku
	port = int(environ.get("PORT", 5000))
	# run the app available anywhere on the network, on debug mode
	app.run(host="0.0.0.0", port=port, debug=True)
	# app.run(debug=True)
