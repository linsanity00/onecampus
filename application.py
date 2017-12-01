# python file that handles the html pages

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

db = SQL("sqlite:///database.db")

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():

    # query database to get a list of dictionaries of the user's clubs
    clubIDs = db.execute("SELECT clubID FROM userClubs WHERE userID = :id", id=session["user_id"])

    # define a list of club names
    clubs = []

    # for each ID in clubIDs, get the club name
    for IDdict in clubIDs:
        clubID = IDdict["clubID"]
        clubs.append(db.execute("SELECT clubName, id FROM clubs WHERE id = :clubID", clubID=clubID)[0])

    # create a list of private events and their information (all events for the user's clubs marked as private)
    privateEvents = db.execute("SELECT eventName, date, time, location, clubName, description, type FROM event INNER JOIN users ON users.id=event.userID WHERE type = :type AND userID = :userID", userID=session["user_id"], type="private")

    # send HTML template the list of club names
    return render_template("dashboard.html", clubs = clubs, privateEvents = privateEvents)

@app.route("/login", methods=["GET", "POST"])
def user():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get
                          ("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/club/<id>")
def club(id):

    # get all information about the club
    clubInfo = db.execute("SELECT * FROM clubs WHERE id = :id", id=id)

    if not clubInfo:
        return apology("Club does not exist", 400)

    return render_template("club.html", clubInfo = clubInfo[0])

@app.route("/user")
def userProfile():
    return render_template("user.html")

@app.route("/findclubs", methods=["GET", "POST"])
def findClubs():
    if request.method == "POST":
        return render_template("findclubs.html")



    else:
        return render_template("findclubs.html")

@app.route("/events", methods=["GET", "POST"])
def events():

    # create a list of private events and their information (all events for the user's clubs marked as private)
    privateEvents = db.execute("SELECT eventName, date, time, location, clubName, description, type FROM event INNER JOIN users ON users.id=event.userID WHERE type = :type AND userID = :userID", userID=session["user_id"], type="private")

    # create a list of public events (all events marked as public)
    publicEvents = db.execute("SELECT eventName, date, time, location, clubName, description, type FROM event WHERE type = :type", type="public")

    return render_template("events.html", privateEvents=privateEvents, publicEvents=publicEvents)

@app.route("/createclub", methods=["GET", "POST"])
def createclub():
    if request.method == "POST":
        clubName = request.form.get("clubName")
        description = request.form.get("description")
        meetingTimes = request.form.get("meetingTimes")
        location = request.form.get("location")
        contact = request.form.get("contact")
        category = request.form.get("category")

        if not clubName or not description or not meetingTimes or not location or not contact:
            return apology("Missing input", 400)

        # Check to make sure the club does not already exist
        # clubID = db.execute("SELECT clubName FROM clubs WHERE clubName = :clubName", clubName=clubName)
        # if clubName:
            # return apology("Club already exists", 400)

        # Insert club into database
        db.execute("INSERT INTO clubs (clubName, description, meetingTimes, location, contact) VALUES(:clubName, :description, :meetingTimes, :location, :contact)", clubName=clubName, description=description, meetingTimes=meetingTimes, location=location,contact=contact)


        # Determine the clubID from clubName
        clubID = db.execute("SELECT id FROM clubs WHERE clubName = :clubName", clubName=clubName)[0]["id"]


        db.execute("INSERT INTO category (category, clubID) VALUES(:category, :clubID)", category=category, clubID=clubID)

        # Add club to user's information in database
        db.execute("INSERT INTO userClubs (userID, clubID) VALUES(:userID, :clubID)",
            userID=session["user_id"], clubID=clubID)

        # Make user an admin
        db.execute("INSERT INTO admins (userID, clubID) VALUES(:userID, :clubID)",
            userID=session["user_id"], clubID=clubID)

        return redirect("/")

    else:
        return render_template("createclub.html")

@app.route("/editclub", methods=["GET", "POST"])
def editclub():
    if request.method == "POST":
        clubName = request.form.get("clubName")
        description = request.form.get("description")
        location = request.form.get("location")
        meetingTimes = request.form.get("meetingTimes")
        nextMeeting = request.form.get("nextMeeting")
        notification = request.form.get("notification")
        notes = request.form.get("notes")
        contact = request.form.get("contact")

        # if not clubName or not description or not location or not meetingTimes or not nextMeeting or not notification or not notes:
        #     return apology("Missing input", 400)

        db.execute("UPDATE clubs SET description = :description, location = :location, meetingTimes = :meetingTimes, nextMeeting = :nextMeeting, notification = :notification, notes = :notes WHERE clubName = :clubName", clubName=clubName, description=description, location=location, meetingTimes=meetingTimes, nextMeeting=nextMeeting,
                notification=notification, notes=notes)

        return redirect("/club")

    else:
        # dropdown menu output
        # Array that stores user's clubs they administrate
        clubNames = []

        # Query portfolio for user's clubs
        names = db.execute("SELECT clubName FROM clubs INNER JOIN admins ON admins.clubID=clubs.id WHERE userID=:userID", userID=session["user_id"])
        print(names)

        # Append to list of all stocks (for dropdown menu)
        for name in names:
            clubNames.append(name)


    return render_template("editclub.html", clubNames=clubNames)

@app.route("/addevent", methods=["GET", "POST"])
def addevent():
    if request.method == "POST":
        clubName = request.form.get("clubName")
        eventName = request.form.get("eventName")
        date = request.form.get("date")
        time = request.form.get("time")
        location = request.form.get("location")
        description = request.form.get("description")
        type = request.form.get("type")

        db.execute("INSERT INTO event (userID, clubName, eventName, date, time, location, description, type) VALUES(:userID, :clubName, :eventName, :date, :time, :location, :description, :type)", userID=session["user_id"], clubName=clubName, eventName=eventName, date=date, time=time, location=location, description=description, type=type)

        return redirect("/")

    else:
        # dropdown menu output
        # Array that stores user's clubs they administrate
        clubNames = []

        # Query portfolio for user's clubs
        names = db.execute("SELECT clubName FROM clubs INNER JOIN admins ON admins.clubID=clubs.id WHERE userID=:userID", userID=session["user_id"])
        # print(names)

        # Append to list of all stocks (for dropdown menu)
        for name in names:
            clubNames.append(name)

    return render_template("addevent.html", clubNames=clubNames)


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/notifications")
def notifications():
    return render_template("notifications.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("password_confirmation")

        email = request.form.get("email")
        school = request.form.get("school")
        year = request.form.get("year")

        # Ensure username was submitted
        if not username:
            return apology("Must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("Must provide password", 400)

        # Ensure confirmation password was submitted
        elif not password_confirmation:
            return apology("Must provide confirmation password", 400)

        elif not password == password_confirmation:
            return apology("Passwords must match", 400)

        # Insert user into database
        rows = db.execute("INSERT INTO users (username, hash, email, school, year) VALUES(:username, :hash, :email, :school, :year)",
                          username=username, hash=generate_password_hash(password), email=email, school=school, year=year)

        # User already exists
        if not rows:
            return apology("Username already taken", 400)

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("register.html")

@app.route("/becomeadmin", methods=["GET", "POST"])
def becomeadmin():
    if request.method == "POST":
        clubName = request.form.get("clubName")

        if not clubName:
            return apology("Missing Input", 400)

        clubID = db.execute("SELECT id FROM clubs WHERE clubName=:clubName", clubName=clubName)[0]["id"]

        db.execute("INSERT INTO admins (userID, clubID) VALUES(:userID, :clubID)", userID=session["user_id"], clubID=clubID)

        return redirect("/")

    else:
        # dropdown menu output
        # Array that stores clubnames
        clubNames = []

        # Query portfolio for user's clubs
        names = db.execute("SELECT clubName FROM clubs")

        # Append to list of all stocks (for dropdown menu)
        for name in names:
            clubNames.append(name)

    return render_template("becomeadmin.html", clubNames=clubNames)

