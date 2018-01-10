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
@login_required
def dashboard():
    return render_template("dashboard.html")

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

@app.route("/myclubs")
def myclubs():
    return render_template("myclubs.html")

@app.route("/club")
def club():
    return render_template("club.html")

@app.route("/user")
def userProfile():
    return render_template("user.html")

@app.route("/addclub", methods=["GET", "POST"])
def addclub():
    if request.method == "POST":
        clubName = request.form.get("clubName")
        description = request.form.get("description")
        meetingTimes = request.form.get("meetingTimes")
        location = request.form.get("location")
        contact = request.form.get("contact")

        if not clubName or not description or not meetingTimes or not location or not contact:
            return apology("Missing input", 400)

        # Insert club into database
        db.execute("INSERT INTO clubs (clubName, description, meetingTimes, location, contact) VALUES(:clubName, :description, :meetingTimes, :location, :contact)",
                        clubName=clubName, description=description, meetingTimes=meetingTimes, location=location,contact=contact)

        # Add club to user's information in database




        return redirect("/")

    else:
        return render_template("addclub.html")




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

        if not clubName or not description or not location or not meetingTimes or not nextMeeting or not notification or not notes:
            return apology("Missing input", 400)

        db.execute("UPDATE users SET description = :description location = :location meetingTimes = :meetingTimes nextMeeting = :nextMeeting notification = :notification notes = :notes WHERE clubName = :clubName", clubName=clubName, description=description, location=location, meetingTimes = meetingTimes, nextMeeting = nextMeeting,
                notification = notification, notes = notes)

        return redirect("/")


    else:
#         # dropdown menu output
         # Array that stores user's clubs they administrate
#         clubNames = []

#         # Query portfolio for user's clubs
#         clubNames = db.execute(
#             "SELECT clubName FROM clubs WHERE id = :id", id=session["user_id"])




#             SELECT Name FROM Invoice
# INNER JOIN InvoiceLine ON Invoice.InvoiceId=InvoiceLine.InvoiceId
# INNER JOIN Track ON InvoiceLine.TrackId=Track.TrackId
# WHERE Invoice.CustomerId=50

#         # Append to list of all stocks (for dropdown menu)
#         for symbol in stocks:
#             # Ensures user has shares of stock
#             if symbol["SUM(shares)"] != 0:
#                 symbols.append(symbol["symbol"])
        return render_template("editclub.html")

@app.route("/addevent")
def addevent():
    return render_template("addevent.html")

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


