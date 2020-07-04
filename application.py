import os
from flask import Flask, session, render_template, request, g, jsonify, json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from flask_login import login_required, LoginManager, UserMixin, login_user
import requests

app = Flask(__name__)
app = Flask(__name__,template_folder=r"C:\Users\Ruhan\Python\Lib\site-packages\jinja2")
app.secret_key = "qwixnxmwo165/*xan"

conn = psycopg2.connect("host=ec2-52-70-15-120.compute-1.amazonaws.com dbname=df44sa70pig1i1 user=znigfbuzkfpomr password=91d462e393b048ad4d5fef35bc1ac55e8c7486e6f9c93d99164d8af9d267b564")
cursor = conn.cursor()

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/", methods=["GET","POST"])
def index():
    #GET request
    if request.method == "GET":
        return render_template("index.html")

    #POST request
    if request.method == "POST":

        #Check if username not empty
        if not request.form.get("username"):
            return render_template("apology.html", name="Username not provided")

        #Check if email not empty
        if not request.form.get("email"):
            return render_template("apology.html", name="Email not provided")

        #Check if password not empty
        if not request.form.get("password"):
            return render_template("apology.html", name="Password not provided")

        #Check if confirm password not empty
        if not request.form.get("confirmpassword"):
            return render_template("apology.html", name="Password not provided")

        #Check if passwords match
        if request.form.get("password") != request.form.get("confirmpassword"):
            return render_template("index.html", wrong="Error: The Passwords entered do not match")

        #hash the user's password
        hashed_password = generate_password_hash(request.form.get("password"))

        #Check if username exists in the database
        usernames = db.execute("SELECT username FROM userdetails")
        username_check = list()
        for username in usernames:
            users_name = username['username']
            if users_name not in username_check:
                username_check.append(users_name)

        if request.form.get("username") in username_check:
            return render_template("index.html", wrong="Error: The Username entered already exists")
        else:
            new_query = """INSERT INTO userdetails (username, email, password) VALUES (%s, %s, %s)"""
            data_to_insert = (request.form.get("username"), request.form.get("email"), hashed_password)
            cursor.execute(new_query, data_to_insert)
            conn.commit()
            return render_template("apology.html", name="Inserted username into the table and redierct to search page")

@app.route("/login", methods=["GET","POST"])
def login():
    #Forget any user_id
    session.pop("user", None)

    #GET request
    if request.method == "GET":
        return render_template("login.html")

    #POST request
    if request.method == "POST":
        #Check if the username is empty
        if not request.form.get("username"):
            return render_template("apology.html", name="Please provide a username")

        #Check if the password is empty
        if not request.form.get("password"):
            return render_template("apology.html", name="Please provide a password")

        #Check if the username exists in the database
        usernames = db.execute("SELECT username FROM userdetails")
        username_check = list()
        for username in usernames:
            users_name = username['username']
            if users_name not in username_check:
                username_check.append(users_name)

        #Check if the username and the password match
        if request.form.get("username") in username_check:
            passwords = "SELECT password from userdetails WHERE username = %s"
            cursor.execute(passwords, (request.form.get("username"),))
            password_check = cursor.fetchone()

            #Check if the password matches
            if check_password_hash(password_check[0], request.form.get("password")):

                #Remember which user has logged in
                session["user"] = request.form.get("username")
                return render_template("search.html", name=session["user"])

            else:
                #Incorrect password so, apology
                return render_template("login.html", wrong= "Error: The entered Username and Password do not match")

        else:
            #Username and password dont match so, apology
            return render_template("login.html", name="Username and password don't match")

@app.route("/search", methods=["GET","POST"])
def search():
    if g.user:
        #GET request
        if request.method == "GET":
            return render_template("search.html", name=session["user"])

        #POST request
        if request.method == "POST":
            #Check if valid input given by the user_id
            if not request.form.get("searchname"):
                return render_template("apology.html", name="Please provide a search method to search for a book")

            #Create a JSON object
            x = jsonify(isbn= "ISBN",
            title= "Title",
            author= "Author",
            year= "Year")


            # Search using isbn
            if request.form.get("searchby") == "isbn":
                data = cursor.execute("SELECT * FROM bookdetails WHERE isbn LIKE '%{}%'".format(request.form.get("searchname")))
                data_results = cursor.fetchall()
                if not data_results:
                    return render_template("search.html", name1="Book not in database", name=session["user"])
                return render_template("search.html", name=session["user"], y=x, results=data_results)

            # Search using author
            if request.form.get("searchby") == "author":
                data = cursor.execute("SELECT * FROM bookdetails WHERE author LIKE '%{}%'".format(request.form.get("searchname")))
                data_results = cursor.fetchall()
                if not data_results:
                    return render_template("search.html", name1="Book not in database", name=session["user"])
                return render_template("search.html", name=session["user"], isbn1="ISBN", title1="Title", author1="Title", year1="Year", reviews1="Reviews", results=data_results)

            # Search using title
            if request.form.get("searchby") == "title":
                data = cursor.execute("SELECT * FROM bookdetails WHERE title LIKE '%{}%'".format(request.form.get("searchname")))
                data_results = cursor.fetchall()
                if not data_results:
                    return render_template("search.html", name1="Book not in database", name=session["user"])
                return render_template("search.html", name=session["user"], isbn1="ISBN", title1="Title", author1="Title", year1="Year", reviews1="Reviews", results=data_results)

    return render_template("apology.html", name="Unauthorized Access")

@app.route("/searchresult", methods=["GET","POST"])
def searchresult():
    if g.user:

        #GET request
        if request.method == "GET":
            return render_template("searchresult.html")

        #POST request
        if request.method == "POST":
            data = "SELECT * FROM bookdetails WHERE title = %s"
            cursor.execute(data, (request.form.get("review"),))
            data_results = cursor.fetchall()

            #Retrieve reviews for the books
            review_data = "SELECT review FROM bookreviews WHERE book = %s"
            cursor.execute(review_data, (request.form.get("review"),))
            bookdata_results = cursor.fetchall()
            booklist = list()
            for result in bookdata_results:
                if result not in booklist:
                    booklist.append(result[0])

            #Retrieve name of people who inserted reviews
            name_data = "SELECT username FROM bookreviews WHERE book = %s"
            cursor.execute(name_data, (request.form.get("review"),))
            namedata_results = cursor.fetchall()
            namelist = list()
            for result in namedata_results:
                if result not in namelist:
                    namelist.append(result[0])

            #Make a dictionary of review:name
            review_name = dict(zip(booklist, namelist))

            if not data_results:
                return render_template("apology.html", name="error review")
            return render_template("review.html", isbn=data_results[0][0], title=data_results[0][1], author=data_results[0][2], year=data_results[0][3], reviews_names=review_name)

    return render_template("apology.html", name="Unauthorized Access")

@app.before_request
def before_request():
    g.user = None
    if "user" in session:
        g.user = session["user"]

@app.route("/logout")
def logout():
    session.pop("user", None)
    return render_template("login.html")

@app.route("/review", methods=["GET","POST"])
def review():
    if g.user:
        #GET request
        if request.method == "GET":
            return render_template("review.html")

        #POST request
        if request.method == "POST":
            check_query = "SELECT * FROM bookreviews WHERE username = %s AND book = %s"
            data_check = (g.user, request.form.get("bookname"))
            cursor.execute(check_query, data_check)
            data_results = cursor.fetchall()

            #Retrieve reviews for the books
            review_data = "SELECT review FROM bookreviews WHERE book = %s"
            cursor.execute(review_data, (request.form.get("bookname"),))
            bookdata_results = cursor.fetchall()
            booklist = list()
            for result in bookdata_results:
                if result not in booklist:
                    booklist.append(result[0])

            #Retrieve name of people who inserted reviews
            name_data = "SELECT username FROM bookreviews WHERE book = %s"
            cursor.execute(name_data, (request.form.get("bookname"),))
            namedata_results = cursor.fetchall()
            namelist = list()
            for result in namedata_results:
                if result not in namelist:
                    namelist.append(result[0])

            #Make a dictionary of review:name
            review_name = dict(zip(booklist, namelist))

            data = "SELECT * FROM bookdetails WHERE title = %s"
            cursor.execute(data, (request.form.get("bookname"),))
            data_results = cursor.fetchall()

            #Insert user's review into the database if a feedback not submitted
            if g.user not in namelist:
                new_query = "INSERT INTO bookreviews (book, username, review) VALUES (%s, %s, %s)"
                data_to_insert = (request.form.get("bookname"), g.user, request.form.get("reviewbox"))
                cursor.execute(new_query, data_to_insert)
                conn.commit()
                return render_template("review.html", isbn=data_results[0][0], title=data_results[0][1], author=data_results[0][2], year=data_results[0][3], name="Feedback submitted!", reviews_names=review_name)
            else:
                return render_template("review.html", isbn=data_results[0][0], title=data_results[0][1], author=data_results[0][2], year=data_results[0][3], name="Error: Already submitted a feedback!", reviews_names=review_name)

    return render_template("search.html", name=session["user"])

@app.route("/goodreads", methods=["GET","POST"])
def goodreads():
    if g.user:
        #GET request
        if request.method == "GET":
            return render_template("goodreads.html")

        #POST request
        if request.method == "POST":

            #Check if valid input given by the user
            if not request.form.get("isbnname"):
                return render_template("apology.html", name="Please provide an isbn to search for a book")

            #Get reviews from goodreads
            isbnname = request.form.get("isbnname")
            res = requests.get("https://www.goodreads.com/book/review_counts.json?", params={"key": "v5IG7bJC3O76oBPp8vf5A", "isbns": isbnname})

            if not res:
                return render_template("goodreads.html", error_message="Data not available")

            return render_template("goodreads.html", data=res.json()["books"][0], id= res.json()["books"][0]["id"], isbn= res.json()["books"][0]["isbn"], isbn13= res.json()["books"][0]["isbn13"], ratings_count= res.json()["books"][0]["ratings_count"], reviews_count= res.json()["books"][0]["reviews_count"], text_reviews_count= res.json()["books"][0]["text_reviews_count"], work_ratings_count= res.json()["books"][0]["work_ratings_count"], work_reviews_count= res.json()["books"][0]["work_reviews_count"], work_text_reviews_count= res.json()["books"][0]["work_text_reviews_count"], average_rating= res.json()["books"][0]["average_rating"])

        return render_template("goodreads.html", data="Goodreads link works")

@app.route("/api/<isbn>", methods=["GET"])
def api(isbn):
    data=isbn

    #query to fetch ISBN from the database
    query = "SELECT * FROM bookdetails WHERE isbn = '{}'".format(data)
    cursor.execute(query, data,)
    results = cursor.fetchall()

    #get goodreads data
    res = requests.get("https://www.goodreads.com/book/review_counts.json?", params={"key": "v5IG7bJC3O76oBPp8vf5A", "isbns": results[0][0]})

    #404 if ISBN not in databse
    if not query:
        return render_template("apology.html", name="404")

    return jsonify(title= results[0][1],author= results[0][2],year= results[0][3],
    isbn= results[0][0],
    review_count= res.json()["books"][0]["reviews_count"],
    average_score= res.json()["books"][0]["average_rating"])
