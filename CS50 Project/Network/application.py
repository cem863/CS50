# I will import the libraries that I will use in my project
import datetime
from datetime import timedelta
import re

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from helpers import apology, login_required

# I configure the flask application here
app = Flask(__name__)

# I configure the app using flask_mail documntation. The bot that will send emails to the user's friends is called "sendertrial54321@gmail.com"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
app.config['MAIL_USERNAME'] = 'sendertrial54321@gmail.com'
app.config['MAIL_PASSWORD'] = 'ThisisCS50'

# I connect the mail class to the app
mail = Mail(app)


# This piece of code is extracted from finance. I ensure that responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# This piece of code is extracted from finance. I store sessions on the local filesystem 
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# I configure will be using a SQLite database. I will use a database called "finance.db" (for reasons discussed with my TA). 
# Yet, this database is used for a different application to finance and its contents are different.
db = SQL("sqlite:///finance.db")


# I globally define priority, frequency, and friend type options. These are the options that the user will be able to choose when 
# adding a new friend to their list of friends
PRIORITY = ['High', 'Low']
FREQUENCY = ['1 minute', '1 week', '1 month', '3 months']
# Below are the number of minutes for each option. This will prove to be practical later on
FREQUENCY_VALUES = [1, 10080, 43800, 131400]
TYPE = ['Friend', 'Acquaintance', 'Family Member', 'Colleague', 'Professional Connection']


# I create the route /main. This corresponds to the home page of the website. 
@app.route("/main") 
@login_required
def main():
    return render_template("main.html")

# I create the route /. This will correspond to the index.html page. Here, the user will see a full list of their friends


@app.route("/")
@login_required
def index():

    # Get a list of dictionaries with the names of the user's friends
    names = db.execute(
        "SELECT friend_name FROM transactions WHERE investor_id = ?", session["user_id"])
        
    # Get a list of dictionaries to show popup notifications when user is on home page. These popup notifications will let the user know which 
    # friends they have to each out to. This will happen when they miss a deadline.
    current_time = datetime.datetime.now()
    popup_names = db.execute(
        "SELECT friend_name, friend_id, reachout_deadline, priority FROM transactions WHERE investor_id = ? AND ? > reachout_deadline ORDER BY priority ASC", session["user_id"], current_time)
    
    # I pass these lists of dictionaries to index.html
    return render_template("index.html", names=names, popup_names=popup_names)
    
    
# I create the route /buy. This route allows the user to add friends to their list. When using GET request, the user will see a form where they 
# can 'add' a friend to their list. When using POST request, the database.db will add a new row containing the information of the newly added friend 
# The route is called /buy for reasons mentioned previously. 
@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    # If POST, then insert a new row to the "transactions" table, containing the information that the user provided in the form
    if request.method == "POST":
        
        # Check that the user has entered a friend
        input_friend = request.form.get("friend_name")
        if (not input_friend):
            return apology("Please enter the friend name")
        
        # Check that the user has entered an email
        input_email = request.form.get("friend_email")
        if (not input_email):
            return apology("Please enter the friend's email")
            
        # Check that the user has entered what the friend likes
        input_food = request.form.get("friend_food")
        if (not input_food):
            return apology("Please enter the friend's favorite food")
            
        # Check that the user has entered where they met their friend
        input_where = request.form.get("friend_where")
        if (not input_where):
            return apology("Please enter where you met this friend")
            
        # Check that the user has classified their friedn
        input_type = request.form.get("type")
        if (not input_type or input_type not in TYPE):
            return apology("Please a valid type of relationship with this person")
        
        # Check that the user has set a priority level to their friend
        input_priority = request.form.get("priority")
        if (not input_priority or input_priority not in PRIORITY):
            return apology("Please enter a valid friend's priority")
  
        # Check that the user has entered a frequency level to reach out to their friend
        input_frequency = request.form.get("frequency")
        print(input_frequency)
        if (not input_frequency or input_frequency not in FREQUENCY):
            return apology("Please enter a valid friend's frequency to reach out to")

        # Store friend information on "transactions" table and show that to the user. 
        # Insert into the table the selected level of frequency. Since we must be consistent with time
        # units (here I only use minutes). Then I use a FREQUENCY and FREQUENCY_VALUES table. This way
        # when user selects a "3-month" frequency, the website knows what the time is in minutes.
        # I chose this method because my options are discrete (the user does not have the freedom to select
        # an infinite number of frequency levels)
        for counter in range(len(FREQUENCY)):
            if input_frequency == FREQUENCY[counter]:
                db.execute(
                    "INSERT INTO transactions (friend_name, date_time, investor_id, reachout_deadline, friend_email, friend_food, friend_where, priority, frequency, friend_type) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", input_friend, datetime.datetime.now(), session["user_id"], datetime.datetime.now() + timedelta(minutes=FREQUENCY_VALUES[counter]), input_email, input_food, input_where, input_priority, FREQUENCY_VALUES[counter], input_type)
       
        # Take user to the original list of friends
        return redirect('/')

    else:
        
        # If GET, display a form where the user can input friend information
        return render_template("prebuy.html", priorities=PRIORITY, frequencies=FREQUENCY, types=TYPE)

# I create the route /eachfriendinfo. This allows the user to see friend-specific information for each friend.


@app.route("/eachfriendinfo", methods=["GET", "POST"])
def eachfriendinfo():
    
    # If POST, then the user sends a reachout email to their friend
    if request.method == "POST":
        
        # To identify what friend to email and update the new reachout deadline (right after sending the email)
        # we need the friend ID
        friend_id = request.form.get("friend_id")
        frequency_list = db.execute(
            "SELECT frequency FROM transactions WHERE friend_id = ? AND investor_id = ?", friend_id, session["user_id"])
        frequency = frequency_list[0]['frequency']
        
        # Get pythonic variables containing the friend's email, name, and meeting place from the database
        email_list = db.execute(
            "SELECT friend_name, friend_email, friend_where FROM transactions WHERE friend_id = ? AND investor_id = ?", friend_id, session["user_id"])
        email = email_list[0]['friend_email']
        meeting_place = email_list[0]['friend_where']
        friend_name = email_list[0]['friend_name']
        print(friend_name)
        print(meeting_place)
        
        # Get user's first name to send with the email
        first_name_list = db.execute(
            "SELECT first_name FROM users WHERE id = ?", session["user_id"])
        first_name = first_name_list[0]['first_name']
 
        # Set up the reachout email that the user can send
        text = "? I was there recently and I remembered the good time we spent together. Anyways, I just wanted to say hi and wish you well!"
        message = "Hi " + friend_name + ", " + first_name + " here. Remember where we met? " + meeting_place + text
        msg = Message("Hi", sender='sendertrial54321@gmail.com', recipients=[email], body=message)
        
        # Send the email to the friend
        mail.send(msg)
            
        # Update the friend's new reachout deadline
        db.execute(
            "UPDATE transactions SET date_time = ?, reachout_deadline = ? WHERE investor_id = ? AND friend_id = ?", datetime.datetime.now(), datetime.datetime.now() + timedelta(minutes=frequency), session["user_id"], friend_id)
            
        # Direct the user to the list of friends that they still need to reach out to
        return redirect('/toreachoutto')
        
    else:
        # To identify what friend to email we need the friend ID
        friend_id = request.args.get("friend_id")
        
        # Extract information from the 'transactions' table and pass it to eachfriendinfo.html
        friendinfo = db.execute(
            "SELECT friend_id, friend_name, reachout_deadline, friend_email, friend_food, friend_where, priority, friend_type FROM transactions WHERE investor_id = ? AND friend_id = ?", session["user_id"], friend_id)
            
        return render_template("eachfriendinfo.html", friendinfo=friendinfo)


# I create the route /toreachoutto. This gathers information from each friend and passes it to the toreachout.html page. The toreachoutto.html page displays
# a list of all the friends that the user needs to reach out to.
@app.route("/toreachoutto")
@login_required
def toreachoutto():
    # Display names of friends. I use the datetime library to know what time it is now and compare it to the reachout deadline, for each friend, stored in the database
    current_time = datetime.datetime.now()
    names = db.execute(
        "SELECT friend_id, friend_name, reachout_deadline, priority FROM transactions WHERE investor_id = ? AND ? > reachout_deadline ORDER BY priority ASC", session["user_id"], current_time)
    return render_template("toreachoutto.html", names=names)
    
    
# I create the route /login. This allows the user to log in. This has been adaptde from finance for the reasons previously mentioned.
@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in. Finally, notice how login “remembers” that a user is logged in by storing his or her user_id, an INTEGER, in session. That way, any of this file’s routes can check which user, if any, is logged in.
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


# I create the route /logout. This logs the user out. This has been adapted from finance for the reasons previously mentioned
@app.route("/logout")
def logout():

    # Forget any user_id. otice how logout simply clears session, effectively logging a user out.
    session.clear()

    # Redirect user to login form
    return redirect("/")


# I create the route /register. This registers the user into the website. This has been adapted from finance for the reasons previously mentioned
@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # If POST, then register the user
    if request.method == "POST":

        # Store field input in pythonic variables
        first_name = request.form.get("first_name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmation")

        # Validate submission
        number_of_repeated_usernames = db.execute("SELECT COUNT(username) FROM users WHERE username = ? ", username)
        number = number_of_repeated_usernames[0]['COUNT(username)']
        print(number)
        if (not first_name) or (not username) or (not password) or (password != confirm_password):
            return apology("You must enter a first name, username and a password. Make sure passwords are consistent", 400)
        if number == 1:
            return apology("Please try a different username. That one is being used already", 400)

        # Hash the password
        hashpassword = generate_password_hash(password)

        # I insert the username and (hashed) password into database
        db.execute(
            "INSERT INTO users (first_name, username, hash) VALUES (?, ?, ?)", first_name, username, hashpassword)
        rows = db.execute("SELECT id FROM users WHERE username = ?", username)

        # Remember which user has logged in. 
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")

    # If GET, then display the registration form
    return render_template("register.html")

# I create the route /sell. This allows the user to "find friends by type". That is, here the user can see a list of all their 
# "family members" or a list of all their "colleagues" and so on. The route is called /sell as it was adapted.


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    
    # If POST, send find all friends of a specific type and show a list of these
    if request.method == "POST":
        friend_type = request.form.get("type")
        
        friendinfo = db.execute(
            "SELECT friend_name FROM transactions WHERE friend_type = ? AND investor_id = ? ", friend_type, session["user_id"])
    
        return render_template("presell.html", friendinfo=friendinfo, types=TYPE)

    else:
        return render_template("presell.html", types=TYPE)

# The errorhandler function was adapted from finance


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# I listen for errors here. This was adapted from finance.
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
