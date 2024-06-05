import os
import smtplib
import secrets 
from PIL import Image
from flask import render_template,url_for, request, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from StoryApp import app,db, bcrypt
from StoryApp.forms import SignUpForm, LogInForm, UpdateProfileForm, RequestResetForm, ResetPasswordForm, SearchForm, DeleteAccountForm
from StoryApp.models import User, initialize_database
from flask_login import login_user, current_user, logout_user,login_required
from flask_mail import Message
import bleach
from bleach import clean
#TZX010# import csv
#TZX010# import pyttsx3   # a simple text-to-speech converter library in Python
from gtts import gTTS                       # TZX010
from sqlalchemy import exc, func , or_           # TZX002
from datetime import datetime               # TZX002
import winsound                             # TZX002
import markdown                             # TZX003
from bs4 import BeautifulSoup               # TZX006
from StoryApp.models import Story           # TZX003a
from StoryApp.models import Comment
from StoryApp.models import Rating          # TZX011a
from flask import Flask, jsonify
# Install the googletrans library using "pip install googletrans==4.0.0-rc1"    # TZX010
from googletrans import Translator              # TZX010
# Install the langdetect libarry: "pip install langdetect"  # TZX010
from langdetect import detect, detect_langs, DetectorFactory        # TZX010
from langdetect.lang_detect_exception import LangDetectException    # TZX010


# CSV file - to store the stories data.
#TZX010# CSV_FILE = 'StoryApp/stories.csv'

# Adjust the maximum content length for Flask Application Configurations.   # TZX010
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit          # TZX010

EditMode = False        # TZX010

# List of supported languages               # TZX010
languages = {                               # TZX010
   # 'zh': 'Chinese',                       # TZX010
    'zh-CN': 'Chinese (Simplified)',        # TZX010
    'zh-TW': 'Chinese (Traditional)',       # TZX010
    'en': 'English',                        # TZX010
    'tl': 'Filipino',                       # TZX010
    'fr': 'French',                         # TZX010
    'de': 'German',                         # TZX010
    'el': 'Greek',                          # TZX010
    'iw': 'Hebrew',                         # TZX010
    'hi': 'Hindi',                          # TZX010
    'id': 'Indonesian',                     # TZX010
    'it': 'Italian',                        # TZX010
    'ja': 'Japanese',                       # TZX010
    'ko': 'Korean',                         # TZX010
    'la': 'Latin',                          # TZX010
    'ms': 'Malay',                          # TZX010
    'pt': 'Portuguese',                     # TZX010
    'ru': 'Russian',                        # TZX010
    'es': 'Spanish',                        # TZX010
    'ta': 'Tamil',                          # TZX010
    'th': 'Thai'                            # TZX010
    # Add more languages if needed          # TZX010
}                                           # TZX010

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

# Retrieves a story from database based on timestamp.           # TZX006
def get_story_by_timestamp(timestamp):                          # TZX002
    return Story.query.filter_by(timestamp=timestamp).first()   # TZX002


#--- TZX006 (Start) ------------------------------------------------------
# Retrieves ALL stories created by specified author.            # TZX006
'''
def get_story_by_author(author):                                # TZX006
    return Story.query.filter_by(author=author).all()           # TZX006
'''
def get_story_by_author(author):                                    # TZX006
    return db.session.query(Story).filter_by(author=author).all()   # TZX006

def markdown_to_plain_text(markdown_text):                          # TZX006
    # Convert markdown to HTML                                      # TZX006
    #html = markdown2.markdown(markdown_text)                       # TZX006
    # Based on testing, markdown2 NOT support "###"                 # TZX006
    # markdown module support "###"                                 # TZX006


    # By default, the markdown module doesn't convert single        # TZX006
    # newlines to <br> tags. We need double newlines.               # TZX006
    #html = markdown.markdown(markdown_text)                         # TZX006
    # NOTE: markdown library not supported "\n"             # TZX006
    # Replace newline characters, "\n" with <br> tags       # TZX006
    text1 = markdown_text                                   # TZX006
    text2 = text1.replace('\\n', '<br>')                    # TZX006
    html = markdown.markdown(text2)                         # TZX006

    # Parse HTML and extract text                   # TZX006
    soup = BeautifulSoup(html, 'html.parser')       # TZX006
    plain_text = soup.get_text()                    # TZX006
    
    return plain_text                               # TZX006
#--- TZX006 (End) ------------------------------------------------------


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

# TZX010 (begin) ------------------------------------------------------------------------------
# Note: The 'translate' library relies on external services for translation. It may use
# different providers like Google Translate, which might have limitations or require an
# API key. If you need more advanced features or support for multiple languages, you might
# consider using the googletrans library, which is a free and unlimited Python library 
# that uses the Google Translate API.
# Limitation: Google Translate API typically enforces a limit on the number of characters 
# per request. This limit can be around 5000 characters. If you try to translate text 
# that exceeds this limit, you may encounter an error.
# Work around Solution: By handling the text in chunks, you can effectively work around 
# the size limitations of the googletrans library and the Google Translate API.
# Accuracy: Splitting the text at arbitrary points can sometimes lead to less accurate 
# translations, especially if it splits sentences or phrases in awkward places. To mitigate 
# this, you can try to split the text at natural boundaries such as spaces or punctuation marks.

def detect_language(text):
    # The DetectorFactory.seed setting ensures that results are consistent across multiple runs.
    DetectorFactory.seed = 0
    try:
        # Detect the language
        language = detect(text)
        print('After detect(text)')
        return language
    except LangDetectException as e:
        # Handle cases where detection fails
        print("Language detection failed: {str(e)}")
        language = 'en'     # Default to English
        return language
    
def split_text(text, max_length=5000):
    # Split the text into chunks of max_length characters
    chunks = []
    while len(text) > max_length:
        # Find the last space within the first `max_length` characters
        split_point = text[:max_length].rfind(' ')

        # If no space is found, split at `max_length`
        if split_point == -1:
            split_point = max_length

        # Add the chunk to the list    
        chunks.append(text[:split_point])

        # Remove the processed chunk from the text
        text = text[split_point:]

    # Add the remaining text as the last chunk    
    chunks.append(text)

    return chunks

def text_to_mp3(text, mp3_filename, language_code):

    # Create the gTTS object
    tts = gTTS(text=text, lang=language_code)

    # Save the audio to a file named "output.mp3"
    tts.save(mp3_filename)

    return 0

# TZX010 (end) ------------------------------------------------------------------------------

# TZX010 - commented the CSV obsolete codes below (begin) -------------------------------------
'''
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
'''
# TZX010 - commented the CSV obsolete codes above (end) -----------------------------------


@app.route('/')
def home():
    return render_template("home.html",title="Home")


@app.route("/login" , methods =["GET","POST"])
def login():
    global username     # TZX002

    if current_user.is_authenticated:
       return redirect(url_for("index"))
    form =LogInForm()

    # We need to keep the username !!!  # TZX004
    username = form.email.data          # TZX004

    # Store username in Session             # TZX011
    session['username'] = username          # TZX011

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

@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        user = User.query.filter_by(id=current_user.id).first()
        if bcrypt.check_password_hash(user.password, form.password.data):
            db.session.delete(user)
            db.session.commit()
            logout_user
            flash('Your account has been successfully deleted.', 'success')
            return redirect(url_for('signup'))
        else:
            flash('Password is incorrect. Please try again.', 'danger')
    return render_template("delete_account.html", title="Delete Account", form=form)
        

@app.route('/success')
def index():
    global EditMode                         # TZX006

    EditMode = False                        # TZX006    
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

    stories = read_from_db()                                    # TZX002
    # Store EditMode in Session                                 # TZX006
    session['EditMode'] = EditMode                              # TZX006

    #return render_template('storylist.html', stories=stories)
    return render_template('storylist.html', stories=stories, editmode=EditMode)    # TZX006


# -- TZX006 (start) -------------------------------------------------------------
# If "Edit" Navigation Menu pressed, route to this "editrecord" function.   # TZX006
@app.route('/editrecord')                                                   # TZX006
def editrecord():                                                           # TZX006

    # Retrieve username from session                                        # TZX010a
    username = session.get('username', "")  # Default to "" if not set      # TZX010a

    try:                                                                    # TZX006
        # This will raise a NameError because 'username' is not defined.    # TZX006
        print(username)                                                     # TZX006
    except NameError:                                                       # TZX006
        flash("An error occurred: 'username' is not defined. Please log in to your account.", "error")     # TZX006
        return render_template('home.html')                                     # TZX006
                
    # Proceed if not NameError...                                               # TZX006
    EditMode = True                                                             # TZX006            
    stories = get_story_by_author(username)                                     # TZX006

    # Store EditMode in Session                                     # TZX006
    session['EditMode'] = EditMode                                  # TZX006

    return render_template('storylist.html', stories=stories, editmode=EditMode)  # TZX006


@app.route('/edit_story/<timestamp>')                               # TZX006
def edit_story(timestamp):                                          # TZX006
    global primary_key                                              # TZX006

    story = get_story_by_timestamp(timestamp)                       # TZX006
    print('story.id:', story.id)                                    # TZX006
    primary_key = story.id                                          # TZX006
    return render_template('edit_story.html', story=story)          # TZX006


# All the following lines are NEW added, not verify yet !!!!            # TZX006 !!!
#@app.route('/update_story/<timestamp>', methods=['GET', 'POST'])       # TZX006
@app.route('/update_story', methods=['POST'])                           # TZX006
def update_story():                                                     # TZX006
    
    # Testing...                                                # TZX006
    #msg = 'Debug msg: primary_key = ' + str(primary_key)        # TZX006 
    #flash(msg, 'success')                                       # TZX006
    #return redirect(url_for('home'))                            # TZX006

    #story = get_story_by_timestamp(timestamp)                           # TZX006
    story = Story.query.get(primary_key)                                # TZX006
    
    if story:                                                           # TZX006
        if request.method == 'POST':                                    # TZX006
            new_content = request.form['content']                       # TZX006
            story.content = new_content                                 # TZX006
            db.session.commit()                                         # TZX006
            flash('Story has been updated successfully!', 'success')    # TZX006
            return redirect(url_for('home'))                            # TZX006
        return render_template('edit_story.html', story=story)          # TZX006
    else:                                                               # TZX006
        flash('Story not found!', 'danger')                             # TZX006
        return redirect(url_for('home'))                                # TZX006

# -- TZX006 (start) -------------------------------------------------------------



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


@app.route('/read_story/<timestamp>')           # TZX002
def read_story(timestamp):                      # TZX002
    global story

    story = get_story_by_timestamp(timestamp)   # TZX002

    #------------------------------------------------------ # TZX003
    # For Markdown changes.                                 # TZX003
    #------------------------------------------------------ # TZX003
    # Reference: https://icecreamcode.org/posts/python/markdown/
    data = {}                                               # TZX003
    data["page_title"] = story.title                        # TZX003
    data["author"] = story.author                           # TZX004
    data["timestamp"] = story.timestamp                     # TZX004

    # Based on my testing, markdown2 module NOT support "###".      # TZX006
    # markdown module support "###"                                 # TZX006
    # By default, the markdown module doesn't convert single        # TZX006
    # newlines to <br> tags. We need double newlines.               # TZX006

    # NOTE: markdown library not supported "\n"             # TZX006
    # Replace newline characters, "\n" with <br> tags       # TZX006
    text1 = story.content                                   # TZX006
    text2 = text1.replace("\\n", "<br>")                    # TZX006
    data["html"] = markdown.markdown(text2)                 # TZX006

    data["back"] = "<a href='/storylist'>Go Back</a>"       # TZX004

    # TZX010 - New changes (begin) ----------------------------------------
    txt1 = story.title     # Retrieve title of story        # TZX010
    txt2 = story.content   # Retrieve the content of story  # TZX010

    # Convert Markdown to readable plain text.              # TZX010
    plain_text = markdown_to_plain_text(txt2)               # TZX010

    # Combine title & content into one variable.            # TZX010
    txt = txt1 + ". " + plain_text                          # TZX010

    # Detect the language                                   # TZX010
    language_code = detect_language(txt)                    # TZX010
    print('Language_code detected:', language_code)         # TZX010

    # Define MP3 filename for TTS audio output.             # TZX010   
    #mp3_filename = ".\static\Audio1.mp3"                    # TZX010
    #mp3_filename = "Audio1.mp3"                            # TZX010a
    mp3_filename = "StoryApp/Audio1.mp3"                   # TZX010a

    # Convert text to speech and save it to mp3 audio file. # TZX010
    text_to_mp3(txt, mp3_filename, language_code)           # TZX010

    # Delete Audio2.MP3 file if exist.              # TZX010
    #file_path = '.\static\Audio2.mp3'               # TZX010
    #file_path = "Audio2.mp3"                             # TZX010a
    file_path = "StoryApp/Audio2.mp3"                   # TZX010a
    if os.path.exists(file_path):                   # TZX010
        os.remove(file_path)                        # TZX010
        print(f'{file_path} has been removed.')     # TZX010
    else:                                           # TZX010
        print(f'{file_path} does not exist.')       # TZX010

    # TZX010 - New changes (end) ---------------------------------------


    #TZX010# return render_template('story_page.html', story=story, data=data)    # TZX005
    return render_template('story_page.html', story=story, data=data, languages=languages)    # TZX010


# TZX010 - Commented the following lines (begin) ---------------------
'''
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

    text1 = story.title             # Retrieve title of story  # TZX002
    engine.say(text1)               # Perform the text-to-speech conversion
    text2 = story.content           # Retrieve the content of story  # TZX002

    # Convert Markdown to readable plain text.  # TZX006
    plain_text = markdown_to_plain_text(text2)  # TZX006
    print(plain_text)                           # TZX006

    #engine.say(text2)               # Perform the text-to-speech conversion
    engine.say(plain_text)          # Perform the text-to-speech conversion # TZX006
    engine.runAndWait()             # Wait for the speech to finish

    return redirect(url_for('read_story', timestamp=timestamp))     # TZX004
'''
# TZX010 (end) ---------------------------------------------------------------------------

# TZX010 (begin) ---------------------------------------------------------------------------
@app.route('/translate', methods=['POST'])
def translate():
    # NOTE: 'translate' library has 500 characters limitation in a single function call.
    # Work around solution: Break down large texts into smaller chunks and translate them individually. 
    # For translate non-English text, ensuring that the text is encoded in UTF-8 encoding can prevent
    # issues with character recognition and translation.
    # Here's a code to translate non-English text Using the googletrans library. 
    #

    # Delete Audio2.MP3 file if exist.              # TZX010
    #file_path = '.\static\Audio2.mp3'               # TZX010
    #file_path = "Audio2.mp3"                        # TZX010a
    file_path = "StoryApp/Audio2.mp3"               # TZX010a
    if os.path.exists(file_path):                   # TZX010
        os.remove(file_path)                        # TZX010
        print(f'{file_path} has been removed.')     # TZX010
    else:                                           # TZX010
        print(f'{file_path} does not exist.')       # TZX010

    try:
        data = request.get_json()
        text = data.get('text')
        target_language = data.get('language')

        print('text:', text)

        if not text or not target_language:
            return jsonify({'error': 'Invalid input or target language'}), 400

        # Detect the language
        language = detect_language(text)

        # Auto-detect language and translate
        try:
            # Create a Translator object
            translator = Translator()

            # Split the text into manageable chunks
            text_chunks = split_text(text)

            # Translate each chunk and combine the results
            translated_chunks = []
            for chunk in text_chunks:
                translated1 = translator.translate(chunk, src=language, dest=target_language).text
                translated_chunks.append(translated1)

            # Combine translated chunks into a single string
            translated_text = ' '.join(translated_chunks)

            # Define MP3 filename for TTS audio output.             # TZX010   
            #mp3_filename = ".\static\Audio2.mp3"                    # TZX010
            #mp3_filename = "Audio2.mp3"                             # TZX010a
            mp3_filename = "StoryApp/Audio2.mp3"                     # TZX010a

            # Convert text to speech and save it to mp3 audio file.         # TZX010
            text_to_mp3(translated_text, mp3_filename, target_language)     # TZX010
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'translation': ''.join(translated_text)})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

# TZX010 (end) ---------------------------------------------------------------------------


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

# Understanding Flask session:                                                      # TZX006
# The session object in Flask is a dictionary-like object that allows you to store  # TZX006 
# information on the server side between requests. This is useful for keeping       # TZX006
# user-specific data across multiple requests (such as during a user session).      # TZX006
# The get method is a built-in Python dictionary method that retrieves a value      # TZX006 
# for a given key. If the key does not exist, it returns a default value.           # TZX006

    # Retrieve EditMode from session                                                # TZX006
    EditMode = session.get('EditMode', False)  # Default to False if not set        # TZX006

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

    return render_template('storylist.html', stories=sorted_records, editmode=EditMode)     # TZX006


# TZX011 (begin) -------------------------------------------------------------------
@app.route('/add_rating', methods=['POST'])
def add_rating():

    # Get data from request.json
    data = request.get_json()
    story_id = data.get("story_id")
    rating1 = data.get("rating")
    rating = int(rating1)
    
    # Retrieve username from session                # TZX011
    user_name = session.get('username', " ")        # TZX011a

    try:
        # Add new rating to the database
        new_rating = Rating(story_id=story_id, rating=rating, username=user_name)
        db.session.add(new_rating)
        db.session.commit()
   
        #TZX011# story = Story.query.get_or_404(story_id)

        # Retrieve ALL the rating for the specific story id.
        ratings = Rating.query.filter_by(story_id=story_id).all()

        #------------------------------------------------------- # TZX012
        # To delete specific record based on id                  # TZX012
        # delrec = Rating.query.filter(Rating.id == 1).first()   # TZX012
        # db.session.delete(delrec)                              # TZX012 
        # db.session.commit()                                    # TZX012
        #------------------------------------------------------- # TZX012
        
        # Compute the average rating based on the unique story id (then round-to-nearest)
        average_rating = round(sum(r.rating for r in ratings) / len(ratings) if ratings else 0, 1)

    except exc.IntegrityError as err:                          
        winsound.Beep(500, 500)
        average_rating = f"Error: {user_name} not found or {err} "

    # Return processed data as JSON
    return jsonify({"average_rating": average_rating})    

# TZX011 (end) ------------------------------------------------------------------------


def initialize_database():
    db.create_all()


''' Commented the following lines for Roel02 changes.
@app.route('/add_comment', methods=['POST'])
def add_comment():
    email = request.form['email']
    comment_text = request.form['comment']
    author = request.form['author']
    
    new_comment = Comment(email=email, comment=comment_text, author=author)
    db.session.add(new_comment)
    db.session.commit()
    
    return jsonify({'status': 'Comment added successfully!'})
'''
# Roel02 (start) -------------------------------------------------------------------
@app.route('/add_comment', methods=['POST'])
def add_comment():

    # Get data from request.json
    data = request.get_json()
    username = data.get("username")
    comment = data.get("comment")
    email = story.author
    timestamp = story.timestamp

    try:
        new_comment = Comment(email=email, comment=comment, author=username, timestamp=timestamp)
        #new_comment = Comment(email=email, comment=commentText, author=author)
        db.session.add(new_comment)
        db.session.commit()
        # Simulate processing the data (replace with your actual logic)
        processed_data = f"Username: {username}, Comment: {comment}"
    except exc.IntegrityError as err:                          
        winsound.Beep(1000, 500)                            
        processed_data = f"Error: {email} {err}"

    # Return processed data as JSON
    return jsonify({"processed_data": processed_data})    
# Roel02 (end) -------------------------------------------------------------------

@app.route('/get_comments', methods=['GET'])
def get_comments():
    comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    return jsonify([{
        'id': comment.id,
        'email': comment.email,
        'comment': comment.comment,
        'author': comment.author,
        'timestamp': comment.timestamp
    } for comment in comments])

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
    app.run(debug=True)

@app.route('/badges')
def badges():
    return render_template('badges.html')

#--- TZX005 -------------------------------------------------------------------