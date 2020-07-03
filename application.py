#for interacting with Operating Systems
import os

from flask import Flask, render_template, flash, session, request, redirect #jsonify, 
from flask_session import Session

#for sqlalchemy connections and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#For password salting, hashing and unhashing
from werkzeug.security import check_password_hash, generate_password_hash

# Allows to send HTTP requests using Python.
import requests

# for using @login_required
#from flask_security import login_required
#from helpers import login_required

app = Flask(__name__)
#app.config['DATABASE_URL'] = "postgres://ukpdswnmbmmcuz:23b8e24df67f99e4c192428081408be924dc1745162bc32bca778db643c70e90@ec2-3-234-109-123.compute-1.amazonaws.com:5432/d6hgmt6gs7ijvf"

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
#@login_required #https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # variable username created for being used in the username select query below
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

        """check_password_hash (pwhash, password) -- checks a password against a given salted and hashed password value 
        :param pwhash: a hashed string like returned by generate_password_hash()
        :param password: the plaintext password to compare against the hash."""

        # Ensure username exists (if the username select query is not None) 
        # Check password is correct by using 'check_password_hash()'
        if result == None or not check_password_hash(result[2], request.form.get("password")):
            return render_template("error.html", message="invalid username and/or password")

        # Remember which user has logged in (columns 0 & 1 from the rows fetched using the above select query)
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

@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

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

        flash('Account created', 'info')

        # Redirect user to login page
        return redirect("/login")   

    else:
        return render_template("register.html")

@app.route("/search", methods=["GET"])
#@login_required
def search():
    """ Get books results """

    # Check book id was provided
    if not request.args.get("book"):
        return render_template("error.html", message="you must provide a book.")

    # Take input and add a wildcard 
    # This wildcard could be used as a search key word
    # Also wildcard is enclosed in '%' to use 'like' operator while preparing SELECT query
    wildcard = "%" + request.args.get("book") + "%"

    # Capitalize first word of wildcard to CAPS and rest to lowercase.
    # This is done because we know the data for Author and Title in books are stored in that format
    # ISBN will not get affected assuming 
    wildcard = wildcard.lower()
    
    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn LIKE LOWER(:wildcard) OR \
                        title LIKE LOWER(:wildcard) OR \
                        author LIKE LOWER(:wildcard) LIMIT 15",
                        {"wildcard": wildcard})
    
    # Books not founded
    if rows.rowcount == 0:
        return render_template("error.html", message="we can't find books with that description.")
    
    # Fetch all the results
    books = rows.fetchall()

    return render_template("results.html", books=books)



# For DB connection using Terminal execute below.
# export DATABASE_URL="postgres://ukpdswnmbmmcuz:23b8e24df67f99e4c192428081408be924dc1745162bc32bca778db643c70e90@ec2-3-234-109-123.compute-1.amazonaws.com:5432/d6hgmt6gs7ijvf"
# export FLASK_DEBUG=1
# export FLASK_APP=application.py
# flask run
# Sample user credentials : herokutest & herokutest1 / admin123+++