#https://youtu.be/pJ8V51XJuf0?si=JHO1ROHlo5-LgVa4 (An introduction to Python and Flask Templates) tutorial video that I learn from and reference from

from flask import Flask, render_template
app = Flask(__name__)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/resetp")
def signup():
    return render_template("forgetpass.html")

if __name__ == "__main__":
    app.run(debug=True) 
   