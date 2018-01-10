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

import datetime
import re

now = datetime.datetime.now()


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
    currenttime = now.strftime("%Y-%m-%d")
    # query database to get a list of dictionaries of the user's clubs
    clubIDs = db.execute("SELECT clubID FROM userClubs WHERE userID = :id", id=session["user_id"])

    # define a list of club names
    clubs = []

    # for each ID in clubIDs, get the club name
    for IDdict in clubIDs:
        clubID = IDdict["clubID"]
        clubs.append(db.execute(
            "SELECT clubName, id FROM clubs WHERE id = :clubID", clubID=clubID)[0])

    # list of events user is going to
    userEvents = db.execute("SELECT * FROM events INNER JOIN userEvents ON events.eventID=userEvents.eventID WHERE userID = :userID AND date >= :currenttime ORDER BY date",
                            userID=session["user_id"], currenttime=currenttime)
    # send HTML template the list of club names
    return render_template("dashboard.html", clubs=clubs, userEvents=userEvents)


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


@app.route("/club/<id>", methods=["GET", "POST"])
def club(id):
    currenttime = now.strftime("%Y-%m-%d")
    if request.method == "GET":
        # get all information about the club
        clubInfo = db.execute("SELECT * FROM clubs WHERE id = :id", id=id)[0]
        events = db.execute(
            "SELECT * FROM clubs INNER JOIN events ON events.clubID = clubs.id WHERE id = :id AND date >= :currenttime ORDER BY date", id=id, currenttime=currenttime)

        if not clubInfo:
            return apology("Club does not exist", 400)

        clubMembers = db.execute(
            "SELECT firstName, lastName, id from users INNER JOIN userClubs ON userClubs.userID = users.id WHERE clubID = :id", id=id)

        return render_template("club.html", clubInfo=clubInfo, events=events, clubMembers=clubMembers)

    else:
        # remove user from club
        db.execute("DELETE FROM userClubs WHERE userID = :userID AND clubID = :clubID",
                   clubID=id, userID=session["user_id"])
        return redirect("/")


@app.route("/user", methods=["GET", "POST"])
def userProfile():
    if request.method == "POST":
        # Get information from the form
        email = request.form.get("email")
        year = request.form.get("year")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        aboutMe = request.form.get("aboutMe")
        facebook = request.form.get("facebook")
        twitter = request.form.get("twitter")

        # Update the user's information based on what they submitted
        db.execute("UPDATE users SET email = :email, year = :year, firstName = :firstName, lastName = :lastName, aboutMe = :aboutMe, facebook = :facebook, twitter = :twitter WHERE id = :userID",
                   userID=session["user_id"], email=email, year=year, firstName=firstName, lastName=lastName, aboutMe=aboutMe, facebook=facebook, twitter=twitter)

        # get an updated list of information about the user
        user = db.execute("SELECT * FROM users WHERE id=:userID",
                          userID=session["user_id"])[0]

        return render_template("user.html", user=user)

    else:
        # get a list of information about the user
        user = db.execute("SELECT * FROM users WHERE id=:userID",
                          userID=session["user_id"])[0]

        return render_template("user.html", user=user)


@app.route("/profile/<id>")
def profile(id):

    # get all information about the user
    userInfo = db.execute("SELECT * FROM users WHERE id = :id", id=id)[0]

    # get all the clubs that the user is in
    userClubs = db.execute(
        "SELECT clubName, id FROM clubs INNER JOIN userClubs ON clubs.id = userClubs.clubID WHERE userID = :id", id=id)

    return render_template("profile.html", userInfo=userInfo, userClubs=userClubs)


@app.route("/findclubs", methods=["GET", "POST"])
def findClubs():
    if request.method == "POST":

        # get the selection type from the dropdown menu
        selection = request.form.get("selection")

        # Join club route
        if not selection:

            clubName = request.form.get("club")

            # Determine the clubID from clubName
            clubID = db.execute("SELECT id FROM clubs WHERE clubName = :clubName",
                                clubName=clubName)[0]["id"]

            # If user is already in club
            if db.execute("SELECT clubID FROM userClubs WHERE clubID=:clubID AND userID=:userID", clubID=clubID, userID=session["user_id"]):
                return apology("You are already a member of " + clubName, 400)
            else:

                # Add club to user's information in database
                db.execute("INSERT INTO userClubs (userID, clubID) VALUES(:userID, :clubID)",
                           userID=session["user_id"], clubID=clubID)
                return redirect("/dashboard")

        # Category dropdown
        else:
            # make lists of clubs by type
            academic = db.execute(
                "SELECT clubName, id FROM clubs WHERE category = :category", category="Academic")
            arts = db.execute(
                "SELECT clubName, id FROM clubs WHERE category = :category", category="Arts")
            service = db.execute(
                "SELECT clubName, id FROM clubs WHERE category = :category", category="Service")
            media = db.execute(
                "SELECT clubName, id FROM clubs WHERE category = :category", category="Media")
            recreation = db.execute(
                "SELECT clubName, id FROM clubs WHERE category = :category", category="Recreation")
            cultural = db.execute(
                "SELECT clubName, id FROM clubs WHERE category = :category", category="Cultural")

            return render_template("findclubs.html", selection=selection, academic=academic, arts=arts, service=service, media=media, recreation=recreation, cultural=cultural)

    else:
        return render_template("findclubs.html")


@app.route("/events", methods=["GET", "POST"])
def events():
    currenttime = now.strftime("%Y-%m-%d")

    # RSVPed
    if request.method == "POST":
        # add to userEvents
        eventID = request.form.get("eventID")
        db.execute("INSERT INTO userEvents (eventID, userID) VALUES (:eventID, :userID)",
                   eventID=eventID, userID=session["user_id"])
        return redirect("/dashboard")

    else:
        # query database to get a list of dictionaries of the user's clubs
        clubIDs = db.execute("SELECT clubID FROM userClubs WHERE userID = :id",
                             id=session["user_id"])

        # list of userevents
        userEvents = []
        # create events of user's clubs
        for IDdict in clubIDs:
            clubID = IDdict["clubID"]
            events = db.execute(
                "SELECT * FROM events WHERE clubID = :clubID AND date >= :currenttime ORDER BY date", clubID=clubID, currenttime=currenttime)
            for event in events:
                userEvents.append(events[0])
        userEvents = sorted(userEvents, key=lambda k: k['date'])

        # create list of all public events not in user's clubs
        publicEvents = db.execute(
            "SELECT * FROM events WHERE type = :type AND date >= :currenttime ORDER BY date", type="public", currenttime=currenttime)

        return render_template("events.html", userEvents=userEvents, publicEvents=publicEvents)


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

        # Insert club into database
        db.execute("INSERT INTO clubs (clubName, description, meetingTimes, location, contact, category) VALUES(:clubName, :description, :meetingTimes, :location, :contact, :category)",
                   clubName=clubName, description=description, meetingTimes=meetingTimes, location=location, contact=contact, category=category)

        # Determine the clubID from clubName
        clubID = db.execute("SELECT id FROM clubs WHERE clubName = :clubName",
                            clubName=clubName)[0]["id"]

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

        db.execute("UPDATE clubs SET description = :description, location = :location, meetingTimes = :meetingTimes, nextMeeting = :nextMeeting, notification = :notification, notes = :notes WHERE clubName = :clubName", clubName=clubName, description=description, location=location, meetingTimes=meetingTimes, nextMeeting=nextMeeting,
                   notification=notification, notes=notes)

        return redirect("/club")

    else:
        # dropdown menu output
        # Array that stores user's clubs they administrate
        clubNames = []

        # Query portfolio for user's clubs
        names = db.execute(
            "SELECT clubName FROM clubs INNER JOIN admins ON admins.clubID=clubs.id WHERE userID=:userID", userID=session["user_id"])

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

        # get clubID
        clubID = db.execute("SELECT id FROM clubs WHERE clubName=:clubName",
                            clubName=clubName)[0]["id"]

        # insert the event into the events table in the database
        db.execute(
            "INSERT INTO events (clubID, eventName, date, time, location, description, type) VALUES(:clubID, :eventName, :date, :time, :location, :description, :type)", clubID=clubID, eventName=eventName, date=date, time=time, location=location, description=description, type=type)

        return redirect("/")

    else:
        # Dropdown menu output
        # Array that stores user's clubs they administrate
        clubNames = []

        # Query portfolio for user's clubs
        names = db.execute(
            "SELECT clubName FROM clubs INNER JOIN admins ON admins.clubID=clubs.id WHERE userID=:userID", userID=session["user_id"])

        # Append to list of all stocks (for dropdown menu)
        for name in names:
            clubNames.append(name)

    return render_template("addevent.html", clubNames=clubNames)


@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")


@app.route("/notifications")
def notifications():

    # get a list of all notifications for the user's clubs
    notifications = db.execute(
        "SELECT notification, clubName FROM clubs INNER JOIN userClubs ON userClubs.clubID=clubs.id WHERE userID=:userID", userID=session["user_id"])

    # append each notification to a list of notifications called notificationsList
    notificationsList = []
    for notification in notifications:
        notificationsList.append(notification)

    return render_template("notifications.html", notificationsList=notificationsList)


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

        # Ensure username not taken
        elif db.execute("SELECT * FROM users WHERE username = :username", username=username):
            return apology("Username already taken", 400)

        # Ensure password was submitted
        elif not password:
            return apology("Must provide password", 400)

        elif not validate(password) == "True":
            return apology(validate(password))

        # Ensure confirmation password was submitted and matches
        elif not password_confirmation:
            return apology("Must provide confirmation password", 400)

        elif not password == password_confirmation:
            return apology("Passwords must match", 400)

        # Ensure the email is a harvard email account
        elif "harvard" not in email:
            return apology("Please enter Harvard email", 400)

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

        # Ensure the user submitted a club name
        if not clubName:
            return apology("Missing Input", 400)

        clubID = db.execute("SELECT id FROM clubs WHERE clubName=:clubName",
                            clubName=clubName)[0]["id"]

        db.execute("INSERT INTO admins (userID, clubID) VALUES(:userID, :clubID)",
                   userID=session["user_id"], clubID=clubID)

        return redirect("/")

    else:
        # Dropdown menu output
        # Array that stores clubnames
        clubNames = []

        # Query portfolio for user's clubs
        names = db.execute("SELECT clubName FROM clubs")

        # Append to list of all stocks (for dropdown menu)
        for name in names:
            clubNames.append(name)

    return render_template("becomeadmin.html", clubNames=clubNames)


def validate(password):
    if len(password) < 8:
        return "Make sure your password is at least 8 characters"
    elif re.search('[0-9]', password) is None:
        return "Make sure your password has a number"
    elif re.search('[A-Z]', password) is None:
        return "Make sure your password has a capital letter"
    elif re.search(r"[ !@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]', password) is None:
        return "Make sure your password has a symbol"
    else:
        return "True"