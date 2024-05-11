# Program name: StoryApp.py
#
# Description: A flask web application for story writer
#
# References:
#  1. Flask – (Creating first simple application)
#      https://www.geeksforgeeks.org/flask-creating-first-simple-application/
#  2. Story Generator App Using Python
#      https://www.geeksforgeeks.org/story-generator-app-using-python/
#  3. How to build a Random Story Generator using Python?
#      https://www.geeksforgeeks.org/how-to-build-a-random-story-generator-using-python/
#  4. HTML Form Elements
#     https://www.w3schools.com/html/html_form_elements.asp
#  5. Python Text To Speech | pyttsx module
#      https://www.geeksforgeeks.org/python-text-to-speech-pyttsx-module/?ref=lbp
#  6. Build a Text to Speech Service with Python Flask Framework
#      https://dev.to/siddheshshankar/build-a-text-to-speech-service-with-python-flask-framework-3966
#  7. Flask - Calling python function on button OnClick event
#      https://stackoverflow.com/questions/42601478/flask-calling-python-function-on-button-onclick-event
#  8. 10 Lines Short Stories With Moral Lessons for Kids
#      https://ofhsoupkitchen.org/short-stories-with-morals#:~:text=The%20Dog%20and%20the%20Bone,a%20bone%20in%20its%20mouth.
#  9. CSS Links
#      https://www.w3schools.com/css/css_link.asp
# 10. CSS Text Shadow
#      https://www.w3schools.com/css/css_text_shadow.asp
#

from flask import Flask, render_template,url_for, request, flash, redirect
from forms import SignUpForm, LogInForm
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt
import csv
import pyttsx3   # a simple text-to-speech converter library in Python
# import os

app = Flask(__name__)
app.config["SECRET_KEY"] = "c1f15fb9b451ddfe14ae6e2baa65d787"

# CSV file - to store the stories data.
CSV_FILE = 'stories.csv'

# print(os.getcwd())

# Function to write story to CSV file
def write_to_csv(title, content):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([title, content])

# Function to read stories from CSV file
def read_from_csv():
    stories = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            stories.append({'title': row[0], 'content': row[1]})
    return stories

# Function to get a single story based on its title
def get_story(title):
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == title:
                return {'title': row[0], 'content': row[1]}
    return None

@app.route("/login" , methods =["GET","POST"])
def login():
    form =LogInForm()
    if form.validate_on_submit():
        if form.username.data =="joel ting" and form.password.data =="ABC123":
            flash("Successfully log in!", "success")
            return redirect(url_for("index"))
        else:
            flash("Log in unsuccessfully.","error")
    return render_template("login.html", title="Log In", form=form)

@app.route("/signup" , methods =["GET","POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        flash(f"Congrats! Account has been successfully created for {form.username.data}!",'success')
        return redirect(url_for("index"))
    return render_template("signup.html",title="Sign Up", form=form)


@app.route("/resetp")
def resetpassword():
    return render_template("forgetpass.html")


@app.route('/')
def index():
    stories = read_from_csv()
    return render_template('index.html', stories=stories)


@app.route('/add_story', methods=['POST'])
def add_story():
    title = request.form['title']
    content = request.form['content']
    write_to_csv(title, content)
    return redirect(url_for('index'))


@app.route('/story/<title>')
def read_story(title):
    global story

    story = get_story(title)
    if story:
        return render_template('story.html', story=story)
    else:
        return "Story not found."


@app.route('/speech_text', methods=['POST'])
#@app.route('/speech_text')
def speech_text():
    
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Setting up voice rate
    engine.setProperty('rate', 125)

    # Setting up volume level between 0 and 1
    engine.setProperty('volume', 0.8)

    # Change voices: 0 for male and 1 for female
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)   # index 0 for male and 1 for female

    text1 = story["title"]          # Retrieve title of story
    engine.say(text1)               # Perform the text-to-speech conversion
    text2 = story["content"]        # Retrieve the content of story
    engine.say(text2)               # Perform the text-to-speech conversion
    engine.runAndWait()             # Wait for the speech to finish

    return render_template('story.html', story=story)


if __name__ == '__main__':
    app.run(debug=True)
