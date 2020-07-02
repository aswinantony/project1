import os

from flask import Flask, render_template, flash, session, request, redirect #jsonify, 

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash

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
#@login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    #flash("This is a flashed message.")
    #flash("Test line 2 flashed message.")

    # Forget any user_id
    session.clear()

    # username field is rendered with an empty string as value.
    username = request.form.get("username")

    #testing password
    password = request.form.get("password")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("error.html", message="must provide password")
    
    #for testing successful login
        if username == "admin" and password == "password":
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

@app.route("/error")
def error():
    return render_template("error.html", message='Sample Error')

# For DB connection using Terminal execute below.
# export DATABASE_URL="postgres://ukpdswnmbmmcuz:23b8e24df67f99e4c192428081408be924dc1745162bc32bca778db643c70e90@ec2-3-234-109-123.compute-1.amazonaws.com:5432/d6hgmt6gs7ijvf"
# export FLASK_DEBUG=1
# export FLASK_APP=application.py
# flask run
# Sample user credentials : herokutest / admin123+++