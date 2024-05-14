from flask import render_template,url_for, request, flash, redirect, request
from StoryApp import app,db, bcrypt
from StoryApp.forms import SignUpForm, LogInForm, UpdateProfileForm
from StoryApp.models import User
from flask_login import login_user, current_user, logout_user,login_required
import csv
import pyttsx3   # a simple text-to-speech converter library in Python
# import os

# CSV file - to store the stories data.
CSV_FILE = 'StoryApp/stories.csv'

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
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form =LogInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash(f"Log in unsuccessfully. Please ensure that you type your username and password correctly.","error")
    return render_template("login.html", title="Log In", form=form)

@app.route("/signup" , methods =["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Congrats! Account has been successfully created for {form.username.data}!",'success')
        return redirect(url_for("login"))
    return render_template("signup.html",title="Sign Up", form=form)


@app.route("/resetp")
def resetpassword():
    return render_template("forgetpass.html")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route("/profile")
#decorator
@login_required
def profile():
    form = UpdateProfileForm()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template("profile.html",title="Profile", image_file=image_file, form=form)


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


