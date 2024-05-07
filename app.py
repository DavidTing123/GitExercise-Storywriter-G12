#https://youtu.be/pJ8V51XJuf0?si=JHO1ROHlo5-LgVa4 (An introduction to Python and Flask Templates) tutorial video that I learn from and reference from

from flask import Flask, render_template,url_for, request, flash, redirect
from forms import SignUpForm, LogInForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "c1f15fb9b451ddfe14ae6e2baa65d787"

@app.route("/")
def home():
    return render_template("home.html",title="Home")

@app.route("/login" , methods =["GET","POST"])
def login():
    form =LogInForm()
    if form.validate_on_submit():
        if form.username.data =="joel ting" and form.password.data =="ABC123":
            flash(f"Successfully log in!")
            return redirect(url_for("home"))
        else:
            flash(f"Log in unsuccessfully.")
            return redirect(url_for("login"))
    return render_template("login.html", title="Log In", form=form)

@app.route("/signup" , methods =["GET","POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        flash(f"Congrats! Account has been successfully created for {form.username.data}!")
        return redirect(url_for("home"))
    return render_template("signup.html",title="Sign Up", form=form)


@app.route("/resetp")
def resetpassword():
    return render_template("forgetpass.html")


if __name__ == "__main__":
    app.run(debug=True) 
