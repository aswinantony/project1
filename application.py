#for interacting with Operating Systems
import os

from flask import Flask, render_template, flash, session, request, redirect, jsonify
from flask_session import Session

#for sqlalchemy connections and session management
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#For password salting, hashing and unhashing
from werkzeug.security import check_password_hash, generate_password_hash

# Allows to send HTTP requests using Python.
import requests

# for using @login_required (custom decorator used, check login_decorator.py )
from login_decorator import login_required

app = Flask(__name__)

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
@login_required #https://flask-login.readthedocs.io/en/latest/#flask_login.login_required
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
@login_required
def search():
    """ Get books results """

    # Check book id was provided 
    # Note: didn't work with request.form.get("book")
    if not request.args.get("book"):
        return render_template("error.html", message="you must provide a book.")

    # Take input and add a wildcard 
    # This wildcard could be used as a search key word
    # Also wildcard is enclosed in '%' to use 'like' operator while preparing SELECT query
    wildcard = "%" + request.args.get("book") + "%"

    # Capitalize first word of wildcard to CAPS and rest to lowercase.
    # This is done because we know the data for Author and Title in books are stored in that format
    # ISBN will not get affected assuming 
    #wildcard = wildcard.title()
    
    # used ILIKE operator to make the select case-insensitive.
    rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                        isbn ILIKE :wildcard OR \
                        title ILIKE :wildcard OR \
                        author ILIKE :wildcard LIMIT 15",
                        {"wildcard": wildcard})
    
    # Books not founded
    if rows.rowcount == 0:
        return render_template("error.html", message="we can't find books with that description.")
    
    # Fetch all the results
    books = rows.fetchall()

    return render_template("results.html", books=books)

@app.route("/book/<isbn>", methods=['GET','POST'])
@login_required
def book(isbn):
    """ Save user review and load same page with reviews updated."""

    if request.method == "POST":
    
        # Save current user info
        currentUser = session["user_id"]
        
        # Fetch form data
        rating = request.form.get("rating")
        comment = request.form.get("comment")

        # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                    {"isbn": isbn})

        # Save id into variable
        id_books = row.fetchone() # (id,)
        bookId = id_books[0]

        # Check for user submission (ONLY 1 review/user allowed per book)
        row2 = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                {"user_id": currentUser,
                 "book_id": bookId})

        # A review already exists
        if row2.rowcount == 1:
            
            flash('You already submitted a review for this book', 'warning')
            return redirect("/book/" + isbn)

        # Convert to save into DB
        rating = int(rating)

        db.execute("INSERT INTO reviews (user_id, book_id, comment, rating) VALUES \
                (:user_id, :book_id, :comment, :rating)",
                {"user_id": currentUser, 
                "book_id": bookId, 
                "comment": comment, 
                "rating": rating})

        # Commit transactions to DB and close the connection
        db.commit()

        flash('Review submitted!', 'info')

        return redirect("/book/" + isbn)
        
    # Take the book ISBN and redirect to his page (GET)
    else:
        row = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                    isbn = :isbn",
                    {"isbn": isbn})

        bookInfo = row.fetchall()

        """ GOODREADS reviews """

        # Read API key from env variable
        key = os.getenv("GOODREADS_KEY")
        
        # Query the api with key and ISBN as parameters
        query = requests.get("https://www.goodreads.com/book/review_counts.json",
                params={"key": key, "isbns": isbn})
        
        # Convert the response to JSON
        json_response = query.json()

        # "Clean" the JSON before passing it to the bookInfo list
        response = json_response['books'][0]

        # Append it as the second element on the list. [1]
        bookInfo.append(response)

        """ Users reviews """

         # Search book_id by ISBN
        row = db.execute("SELECT id FROM books WHERE isbn = :isbn",
                        {"isbn": isbn})

        # Save id into variable
        book = row.fetchone() # (id,)
        book = book[0]

        # TBC this
        # Fetch book reviews
        # Date formatting (https://www.postgresql.org/docs/9.1/functions-formatting.html)
        results = db.execute("SELECT users.username, comment, rating, \
                            to_char(time, 'DD Mon YY - HH24:MI:SS') as time \
                            FROM users \
                            INNER JOIN reviews \
                            ON users.id = reviews.user_id \
                            WHERE book_id = :book \
                            ORDER BY time",
                            {"book": book})

        reviews = results.fetchall()

        return render_template("reviews.html", bookInfo=bookInfo, reviews=reviews)

# API Access: If users make a GET request to your website’s /api/<isbn> route

@app.route("/api/<isbn>", methods=['GET'])
@login_required
def api_call(isbn):

    # COUNT returns rowcount
    # SUM returns sum selected cells' values
    # INNER JOIN associates books with reviews tables

    row = db.execute("SELECT title, author, year, isbn, \
                    COUNT(reviews.id) as review_count, \
                    AVG(reviews.rating) as average_score \
                    FROM books \
                    INNER JOIN reviews \
                    ON books.id = reviews.book_id \
                    WHERE isbn = :isbn \
                    GROUP BY title, author, year, isbn",
                    {"isbn": isbn})

    # Error checking
    if row.rowcount != 1:
        return jsonify({"Error": "Invalid book ISBN"}), 422

    # Fetch result from RowProxy    
    tmp = row.fetchone()

    # Convert to dict
    result = dict(tmp.items())

    # Round Avg Score to 2 decimal. This returns a string which does not meet the requirement.
    # https://floating-point-gui.de/languages/python/
    result['average_score'] = float('%.2f'%(result['average_score']))

    return jsonify(result)

# For DB connection using Terminal execute below.
# export DATABASE_URL="postgres://ukpdswnmbmmcuz:23b8e24df67f99e4c192428081408be924dc1745162bc32bca778db643c70e90@ec2-3-234-109-123.compute-1.amazonaws.com:5432/d6hgmt6gs7ijvf"
# export FLASK_DEBUG=1
# export FLASK_APP=application.py
# flask run
# export GOODREADS_KEY=ujwjG0jOFODfm9vremfHw
# Sample user credentials : herokutest & herokutest1 / admin123+++