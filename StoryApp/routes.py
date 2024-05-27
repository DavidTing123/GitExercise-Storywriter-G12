import os
import smtplib
import secrets 
from PIL import Image
from flask import render_template,url_for, request, flash, redirect
from StoryApp import app,db, bcrypt
from StoryApp.forms import SignUpForm, LogInForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, SearchForm
from StoryApp.models import User
from flask_login import login_user, current_user, logout_user,login_required
from flask_mail import Message
import bleach
from bleach import clean
import csv
import pyttsx3   # a simple text-to-speech converter library in Python
#from pygame import mixer    # Sound effect
## from flask_sqlalchemy import SQLAlchemy     # TZX002
from sqlalchemy import exc, func , or_           # TZX002
from datetime import datetime               # TZX002
import winsound                             # TZX002
import markdown                             # TZX003
from StoryApp.models import Story           # TZX003a


# CSV file - to store the stories data.
CSV_FILE = 'StoryApp/stories.csv'

# Create tables if they don't exist.    # TZX002
with app.app_context():                 # TZX002
    db.create_all()                     # TZX002

# Adds a new story to the database.                             # TZX002
def write_to_db(title, content, author, timestamp):             # TZX002
    try:                                                        # TZX002
        record = Story(title=title, content=content, author=author, timestamp=timestamp)  # TZX002
        db.session.add(record)                                  # TZX002
        db.session.commit()                                     # TZX002
    except exc.IntegrityError as err:                           # TZX002
        winsound.Beep(1000, 500)                            # TZX002
        # check if error is related to author.              # TZX002
        if "author" in str(err):                            # TZX002
            print("Error: Story author cannot be null")     # TZX002

# Retrieves all stories from database.      # TZX002
def read_from_db():                         # TZX002
    all_stories = Story.query.all()         # TZX002
    print('all_stories', all_stories)       # TZX002
    return all_stories                      # TZX002

# Retrieves a story by its title from database.         # TZX002
def get_story_by_timestamp(timestamp):                          # TZX002
    return Story.query.filter_by(timestamp=timestamp).first()   # TZX002

# Deletes a record from database based on timestamp.    # TZX002
def delete_story_by_timestamp(timestamp):               # TZX002
    try:                                                # TZX002
        #story = Story.query.get(timestamp)                  # TZX002
        story = Story.query.filter(Story.timestamp == timestamp).first()    # TZX002
    
        if story:                                           # TZX002
            # Delete the story and commit the change        # TZX002
            db.session.delete(story)                        # TZX002
            db.session.commit()                             # TZX002
            return True                                     # TZX002
        else:                                               # TZX002
            winsound.Beep(1000, 500)                        # TZX002
            print("Timestamp not found.")                   # TZX002
            return False                                    # TZX002
        
    except Exception as e:                                  # TZX002
        print(f"An error occurred while deleting the story: {e}")   # TZX002
        return False                                                # TZX002

# TZX002 program changes (end) ----------------------------------------------------------------

# TZX005 program changes (end) ----------------------------------------------------------------
def get_all_stories():
    return db.session.query(Story).all()  # Retrieve all stories

def sort_stories(field):
    return db.session.query(Story).order_by(getattr(Story, field)).all()  # Sort based on selected field

# TZX005 program changes (end) ----------------------------------------------------------------

# Function to write story to CSV file
def write_to_csv(title, content):
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([title, content])

# Function to read stories from CSV file
def read_from_csv():
    count = 0
    stories = []
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            stories.append({'index': count, 'title': row[0], 'content': row[1]})
            count += 1      # Increment count by 1
    return stories

# Function to get a single story based on its title
def get_story(title):
    with open(CSV_FILE, mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == title:
                return {'title': row[0], 'content': row[1]}
    return None

# Function to delete a single record from the CSV file based record_index.
def delete_csv_record(index):
    # Read the contents of the CSV file
    with open(CSV_FILE, 'r', newline='') as file:
        reader = csv.reader(file)
        data = list(reader)

    # Remove the record at the specified index
    del data[index]

    # Write the updated contents back to the CSV file
    with open(CSV_FILE, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

    return None

@app.route('/')
def home():
    #global username     # TZX001
    
    return render_template("home.html",title="Home")


@app.route("/login" , methods =["GET","POST"])
def login():
    global username     # TZX002

    if current_user.is_authenticated:
       return redirect(url_for("index"))
    form =LogInForm()

    #user = form.username.data       # TZX001
    #password = form.password.data       # TZX001
    #print('User:', user)

    # We need to keep the username !!!  # TZX004
    username = form.email.data          # TZX004
    print('Username:', username)        # TZX004

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash(f"Log in unsuccessfully. Please ensure that you type your email and password correctly.","error")
    return render_template("login.html", title="Log In", form=form)

@app.route("/signup" , methods =["GET","POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SignUpForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, bio='')
        db.session.add(user)
        db.session.commit()
        flash(f"Congrats! Account has been successfully created for {form.username.data}!",'success')
        return redirect(url_for("login"))
    return render_template("signup.html",title="Sign Up", form=form)

@app.route("/logout")
def logout():
    logout_user()
    #return redirect(url_for("index"))
    return redirect(url_for("login"))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext =os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path =os.path.join(app.root_path, "static/profile_pics", picture_fn)
    
    output_size =(256,256)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/profile" , methods =["GET","POST"])
#decorator
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data if form.bio.data else ''
        db.session.commit()
        flash("Your profile has been updated!","success")
        return redirect(url_for('profile'))
    elif request.method =="GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.bio.data = current_user.bio if current_user.bio else ''
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    html_bio = markdown.markdown(current_user.bio or '')
    return render_template("profile.html",title="Profile", image_file=image_file, form=form, html_bio=html_bio)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    posts = []  # Initialize posts as an empty list
    if form.validate_on_submit():
        searched_query = form.searched.data.lower()  # Convert the search query to lowercase
        # Split the search query into individual words
        search_words = searched_query.split()
        # Initialize the query to retrieve stories
        query = Story.query
        # Iterate over each word in the search query
        for word in search_words:
            # Filter stories that contain the word in either the title or the content
            query = query.filter(or_(
                func.lower(Story.title).like(func.lower(f"%{word}%")),
                func.lower(Story.content).like(func.lower(f"%{word}%"))
            ))
        # Execute the query to retrieve the matching stories
        posts = query.order_by(Story.title).all()
        return render_template("search.html", form=form, searched=searched_query, posts=posts)
    return render_template("search.html", form=form, searched="", posts=posts)

@app.context_processor 
def base():
    form = SearchForm()
    return dict(form=form)
        

#@app.route('/')
@app.route('/success')
def index():
#def success():
    #stories = read_from_csv()
    #return render_template('index.html', stories=stories)
    return render_template('index.html')


@app.route('/add_story', methods=['POST'])
def add_story():
    title = request.form['title']
    content = request.form['content']

    # Get the current timestamp                                 # TZX002
    current_timestamp = datetime.now()                          # TZX002
    # Format it as a string (e.g., "YYYY-MM-DD HH:MM:SS")       # TZX002
    DateTime = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")  # TZX002

    try:                                                        # TZX002
        print('username', username)                             # TZX002
    except NameError:                                           # TZX002
        print("The username variable was NOT defined.")         # TZX002
    else:                                                       # TZX002
        print("The username variable was defined.")             # TZX002

    #write_to_csv(title, content)                               # TZX002
    write_to_db(title, content, username, DateTime)             # TZX002

    #return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.route('/storylist')
def storylist():
    #stories = read_from_csv()
    stories = read_from_db()    # TZX002
    return render_template('storylist.html', stories=stories)


@app.route('/archive')
def archive():
    #stories = read_from_csv()
    stories = read_from_db()    # TZX002
    return render_template('archive.html', stories=stories)
    '''
    print("username:", username)
    if username == 'Admin':
        stories = read_from_csv()
        return render_template('archive.html', stories=stories)
    else:
        winsound.Beep(1000, 500)                            # TZX004
        return redirect(url_for('home'))
    '''


#@app.route('/read_story/<title>')
@app.route('/read_story/<timestamp>')           # TZX002
#def read_story(title):
def read_story(timestamp):                      # TZX002
    global story

    #story = get_story(title)
    story = get_story_by_timestamp(timestamp)   # TZX002

    #------------------------------------------------------ # TZX003
    # For Markdown changes.                                 # TZX003
    #------------------------------------------------------ # TZX003
    # Reference: https://icecreamcode.org/posts/python/markdown/
    data = {}                                               # TZX003
    data["page_title"] = story.title                        # TZX003
    data["author"] = story.author                           # TZX004
    data["timestamp"] = story.timestamp                     # TZX004
    data["html"] = markdown.markdown(story.content)         # TZX003
    #data["back"] = "<a href='/storylist'>Back</a>"          # TZX003
    data["back"] = "<a href='/storylist'>Go Back</a>"       # TZX004
    #return render_template('story_page.html', data=data)    # TZX003
    return render_template('story_page.html', story=story, data=data)    # TZX005

'''
    if story:
        return render_template('story.html', story=story)
    else:
        return "Story not found."
'''


#@app.route('/speech_text', methods=['POST'])
#def speech_text():
@app.route('/speech_text/<timestamp>', methods=['POST'])    # TZX004
def speech_text(timestamp):                                 # TZX004

    
    # Initialize the TTS engine
    engine = pyttsx3.init()
    
    # Setting up voice rate
    engine.setProperty('rate', 125)

    # Setting up volume level between 0 and 1
    engine.setProperty('volume', 0.8)

    # Change voices: 0 for male and 1 for female
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)   # index 0 for male and 1 for female

    #text1 = story["title"]          # Retrieve title of story
    text1 = story.title             # Retrieve title of story  # TZX002
    engine.say(text1)               # Perform the text-to-speech conversion
    #text2 = story["content"]        # Retrieve the content of story
    text2 = story.content           # Retrieve the content of story  # TZX002
    engine.say(text2)               # Perform the text-to-speech conversion
    engine.runAndWait()             # Wait for the speech to finish

    #return render_template('story.html', story=story)
    return redirect(url_for('read_story', timestamp=timestamp))     # TZX004


@app.route('/delete_story', methods=['GET', 'POST'])
def delete_story():
    index = 0
    if request.method == "POST":
        # Get the input value from the HTML form
        #record_index = int(request.form.get('button_index'))
        record_timestamp = request.form.get('button_value')     # TZX002 added

        # Process the value as needed (e.g., print it)
        #print(f'Record index is {record_index}')
        print(f'Record timestamp is {record_timestamp}')        # TZX002 changes
        
        #delete_csv_record(record_index)
        delete_story_by_timestamp(record_timestamp)   # TZX002
        
    return redirect(url_for('archive'))

#--- TZX005 -------------------------------------------------------------------
#
@app.route('/sort_record', methods=['GET', 'POST'])
def sort_record():

    '''
    # Available sort fields
    sort_fields = ['title', 'author', 'timestamp']  # Assuming you want to allow sorting by these fields
    '''
    # Available sort fields
    sort_fields = [field.name for field in Story.__table__.columns if field.name != 'id']

    # Default sort field
    selected_field = sort_fields[0]

    # Handle POST request (sort based on selected field)
    if request.method == 'POST':
        selected_field = request.form.get('sort_field')
        sorted_records = sort_stories(selected_field)  # Call a new function for sorting
    else:
        sorted_records = get_all_stories()  # Call a new function to retrieve all stories

    return render_template('storylist.html', stories=sorted_records)

#--- TZX005 -------------------------------------------------------------------
