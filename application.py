import os

from flask import Flask, render_template, flash #request #,session, redirect, , jsonify, 

from flask import Flask, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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

@app.route("/login")
def login():
    #flash("This is a flashed message.")
    #flash("Test line 2 flashed message.")
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/error")
def error():
    return render_template("error.html", message='Sample Error')

# For DB connection using Terminal execute below.
# export DATABASE_URL="postgres://ukpdswnmbmmcuz:23b8e24df67f99e4c192428081408be924dc1745162bc32bca778db643c70e90@ec2-3-234-109-123.compute-1.amazonaws.com:5432/d6hgmt6gs7ijvf"
# export FLASK_DEBUG=1
# export FLASK_APP=application.py
# flask run