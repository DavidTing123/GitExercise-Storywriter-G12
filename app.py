#https://youtu.be/pJ8V51XJuf0?si=JHO1ROHlo5-LgVa4 (An introduction to Python and Flask Templates) tutorial video that I learn from and reference from

from flask import Flask, render_template,request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_login import UserMixin
import MySQLdb.cursors
import re




app = Flask(__name__)


app.config["MYSQL_HOST"] = 'localhost'
app.config["MYSQL_USER"] ='root'
app.config["MYSQL_PASSWORD"] ='Cyc2255!'
app.config["MYSQL_DB"] ='sign up'

mysql = MySQL(app)

@app.route("/" , methods =["GET" , "POST"])
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/resetp")
def resetpassword():
    return render_template("forgetpass.html")

if __name__ == "__main__":
    app.run(debug=True) 
   