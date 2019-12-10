import os, json

from flask import Flask, session, redirect, render_template, request, jsonify, flash
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from operator import itemgetter

from werkzeug.security import check_password_hash, generate_password_hash

import requests

from helpers import login_required

#UPLOAD_FOLDER = '/uploads'
#ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])



app = Flask(__name__)

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#app.config["TEMPLATES_AUTO_RELOAD"] = True

#@app.after_request
#def after_request(response):
#    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#    response.headers["Expires"] = 0
#    response.headers["Pragma"] = "no-cache"
#    return response


# Configure session to use filesystem (instead of signed cookies)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database

# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    """Show homepage"""

    # Display index page

    return render_template("index.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Query database for username
        userCheck = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchone()

        # Check if username already exist
        if userCheck:
            return render_template("error.html", message="username already exist")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Ensure confirmation wass submitted 
        elif not request.form.get("confirmation"):
            return render_template("error.html", message="must confirm password")

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            return render_template("error.html", message="passwords didn't match")
        
        # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)
        
        # Insert register into DB
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :password)",
                            {"username":request.form.get("username"), 
                             "password":hashedPassword})

        # Commit changes to database
        db.commit()

        # Redirect user to login page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Forget any user_id
    session.clear()

    username = request.form.get("username")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")

        # Query database for username (http://zetcode.com/db/sqlalchemy/rawsql/)
        # https://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.ResultProxy
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})
        
        result = rows.fetchone()

        # Ensure username exists and password is correct
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = result[0]
        session["user_name"] = result[1]


        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("login.html")
@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()

    # Redirect user to login form
    return redirect("/")
@app.route("/health")
def health():
    """Display health page"""

    # Render health.html page
    return render_template("health.html")

@app.route("/calorie")
def calorie():
    """Allow users to add calories with date"""

    # Render health.html page
    return render_template("calorie.html")
@app.route("/add", methods=["POST"])
def add():
    """Add calories with date to profile"""
      

    # Ensure username was submitted
    if not request.form.get("calorie"):
        return render_template("error.html", message="Must provide number of calories")

    # Ensure password was submitted
    elif not request.form.get("fecha"):
        return render_template("error.html", message="Must provide date")

    # Get user's ID
    user_id = session["user_id"]
    fecha = request.form.get("fecha")

    # Check if calories for date inputted exists
    exist = db.execute("SELECT * FROM calories WHERE id = :id AND fecha= :fecha", {"id": user_id, "fecha": fecha}).fetchone()

    # Inserts new daily calorie intake if not exist
    if not exist:
        # Insert calorie with date into user's calorie profile
        db.execute("INSERT INTO calories (id, calorie, fecha) VALUES(:id, :calorie, :fecha)",
                    {"id":session["user_id"],"calorie":request.form.get("calorie"), "fecha":request.form.get("fecha")})
        # Redirect user to user's profile page
        db.commit()
        #return redirect("/profile")

    calories = db.execute("SELECT calorie, fecha FROM calories WHERE id = :id", {"id": user_id}).fetchall()
    return render_template("profile.html", calories=calories)

@app.route("/calculator")
def calculator():
    """Display calculator page"""

    # Render calculator.html page
    return render_template("calculator.html")


@app.route("/bmi")
def bmi():
    """Display BMI Calculator"""

    # Render BMI Calculator page
    return render_template("bmi.html")


@app.route("/bmr")
def bmr():
    """Display BMR Calculator"""

    # Render BMR Calculator page
    return render_template("bmr.html")


@app.route("/whr")
def whr():
    """Display WHR Calculator"""

    # Render WHR Calculator page
    return render_template("whr.html")



@app.route("/delete", methods=["POST"])
def delete():
    """Delete calories with date from profile"""

    # Get user's ID
    user_id = session["user_id"]

    # Obtain date of row to be deleted
    fecha = request.form.get("fecha")

    # Delete row
    db.execute("DELETE FROM calories WHERE id = :id AND fecha= :fecha", {"id": user_id, "fecha": fecha})
    db.commit()

    return redirect("/")

@app.route("/profile")
def profile():
    """Display user's profile"""

    # Get user's ID
    user_id = session["user_id"]

    # Obtain user's daily calorie intake
    calories_sort = db.execute("SELECT * FROM calories WHERE id = :id", {"id": user_id}).fetchall()

    # Sort calorie intake in reverse order of date
    calories = sorted(calories_sort, key=itemgetter('fecha'), reverse=True)

    # Display profile page
    return render_template("profile.html", calories=calories)

@app.route("/changeuser", methods=["GET", "POST"])
def changeuser():
    """Allow user to change username"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure new username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="Missing username!")

        # Check if username inputted is unique
        result = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username":request.form.get("username")}).fetchall()


        # Return error if username is taken
        if result:
            return render_template("error.html", message="Username is taken!")

        # Get user's ID
        user_id = session["user_id"]

        # Obtain user's new username
        username = request.form.get("username")

        # Update user's username
        db.execute("UPDATE users SET username = 'username' WHERE id = :id", {"id": user_id})

        db.commit()

        # Query database for user
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                            {"username": username})

        # Remember which user has logged in
        session["user_name"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("changeuser.html")

