#https://youtu.be/pJ8V51XJuf0?si=JHO1ROHlo5-LgVa4 (An introduction to Python and Flask Templates) tutorial video that I learn from and reference from

from flask import Flask, render_template,url_for, request, flash, redirect
from forms import SignUpForm, LogInForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "c1f15fb9b451ddfe14ae6e2baa65d787"

@app.route("/")
def home():
    return "Welcome home!"

@app.route("/login" , methods =["GET","POST"])
def login():
    form =LogInForm()
    return render_template("login.html", title="Log In", form=form)

@app.route("/signup" , methods =["GET","POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", "success")
        return redirect(url_for("home"))
    return render_template("signup.html",title="Sign Up", form=form)


@app.route("/resetp")
def resetpassword():
    return render_template("forgetpass.html")

@app.route("/process", methods=["POST"])
def process():
    return "Congrats! You have successfully sign up as a user. "

if __name__ == "__main__":
    app.run(debug=True) 
   
