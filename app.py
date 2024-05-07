#https://youtu.be/pJ8V51XJuf0?si=JHO1ROHlo5-LgVa4 (An introduction to Python and Flask Templates) tutorial video that I learn from and reference from

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt


app = Flask(__name__)
app.config["SECRET_KEY"] = "c1f15fb9b451ddfe14ae6e2baa65d787"
app.config["SQLALCHEMY_DATABASE_URI"] ="mysql://root:Cyc2255!@localhost:3306/Signup"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db =SQLAlchemy(app)

class Signup (db.Model):
    id = db.Column(db.Integer,primary_key = True)
    email = db.Column(db.String(25))
    username = db.Column(db.String(25))
    password =db.Column(db.String(25))



@app.route("/" , methods =["POST"])
def login():
    return render_template("login.html")

@app.route("/signup" , methods =["POST"])
def signup():
    return render_template("signup.html")

@app.route("/resetp")
def resetpassword():
    return render_template("forgetpass.html")

@app.route("/process", methods=["POST"])
def process():
    email = request.form['email']
    username = request.form['username']
    password= request.form['password']


    return "Congrates! You have successfully sign up as a user. "

if __name__ == "__main__":
    app.run(debug=True) 
   
