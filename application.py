import os
from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import text
from flask_login import login_required, LoginManager, UserMixin, login_user

app = Flask(__name__)
app = Flask(__name__,template_folder=r"C:\Users\Ruhan\Python\Lib\site-packages\jinja2")
app.secret_key = "qwixnxmwo165/*xan"

conn = psycopg2.connect("host=ec2-52-70-15-120.compute-1.amazonaws.com dbname=df44sa70pig1i1 user=znigfbuzkfpomr password=91d462e393b048ad4d5fef35bc1ac55e8c7486e6f9c93d99164d8af9d267b564")
cursor = conn.cursor()

# Configure to use Heroku database
#$env:FLASK_APP = "application.py"
#$env:DATABASE_URL ="postgres://znigfbuzkfpomr:91d462e393b048ad4d5fef35bc1ac55e8c7486e6f9c93d99164d8af9d267b564@ec2-52-70-15-120.compute-1.amazonaws.com:5432/df44sa70pig1i1"


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
            return render_template("apology.html", name="Passwords do not match")

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
            return render_template("apology.html", name="Username already exists")
        else:
            new_query = """INSERT INTO userdetails (username, email, password) VALUES (%s, %s, %s)"""
            data_to_insert = (request.form.get("username"), request.form.get("email"), hashed_password)
            cursor.execute(new_query, data_to_insert)
            conn.commit()
            return render_template("apology.html", name="Insert username into the table and redierct to search page")
            #"""write code to insert user's username into the database"""


@app.route("/login", methods=["GET","POST"])
def login():
    #Forget any user_id
    session.clear()

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
                session["user_id"] = request.form.get("username")
                return render_template("search.html", name=session["user_id"])

            else:
                #Incorrect password so, apology
                return render_template("apology.html", name="Incorrect password")

        else:
            #Username and password dont match so, apology
            return render_template("apology.html", name="username and passwords dont match")

@app.route("/search", methods=["GET","POST"])
def search():
    #GET request
    if request.method == "GET":
        return render_template("search.html", name=session["user_id"])

    #POST request
    if request.method == "POST":
        #Check if valid input given by the user_id
        if not request.form.get("searchname"):
            return render_template("apology.html", name="Please provide a search method to search for a book")

        # Search using isbn
        if request.form.get("searchby") == "isbn":
            data = "SELECT * FROM bookdetails WHERE isbn = %s"
            cursor.execute(data, (request.form.get("searchname"),))
            data_results = cursor.fetchall()
            return render_template("searchresult.html", name=session["user_id"],isbn=data_results[0][0],title=data_results[0][1], author=data_results[0][2], year=data_results[0][3])

        # Search using author
        if request.form.get("searchby") == "author":
            data = "SELECT * FROM bookdetails WHERE author = %s"
            cursor.execute(data, (request.form.get("searchname"),))
            data_results = cursor.fetchall()
            return render_template("searchresult.html", name=session["user_id"],isbn=data_results[0][0], title=data_results[0][1], author=data_results[0][2], year=data_results[0][3])

        # Search using title
        if request.form.get("searchby") == "title":
            data = "SELECT * FROM bookdetails WHERE title = %s"
            cursor.execute(data, (request.form.get("searchname"),))
            data_results = cursor.fetchall()
            return render_template("searchresult.html", name=session["user_id"],isbn=data_results[0][0], title=data_results[0][1], author=data_results[0][2], year=data_results[0][3])
