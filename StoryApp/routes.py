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
from gtts import gTTS                       # TZX010
from sqlalchemy import exc, func , or_     
from datetime import datetime, timedelta    # TZX016
import winsound                             # TZX002
import markdown                             # TZX003
from bs4 import BeautifulSoup               # TZX006
from StoryApp.models import Story           # TZX003a
from StoryApp.models import Comment
from flask import Flask, jsonify
# Install the googletrans library using "pip install googletrans==4.0.0-rc1"
from googletrans import Translator                                  # TZX010
from langdetect import detect, detect_langs, DetectorFactory        # TZX010
from langdetect.lang_detect_exception import LangDetectException    # TZX010
from sqlalchemy import desc                 # TZX015
from sqlalchemy.orm import aliased          # TZX015


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
def write_to_db(data):                                          # TZX014
    try:                                                        # TZX002
        record = Story(**data)                                  # TZX014
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
    return all_stories                      # TZX002


# Retrieves a story from database based on timestamp.           # TZX006
def get_story_by_timestamp(timestamp):                          # TZX002
    return Story.query.filter_by(timestamp=timestamp).first()   # TZX002


def get_story_by_author(author):                                    # TZX006
    return db.session.query(Story).filter_by(author=author).all()   # TZX006


def markdown_to_plain_text(markdown_text):                          # TZX006

    # By default, the markdown module doesn't convert single        # TZX006
    # newlines to <br> tags. We need double newlines.               # TZX006
    # NOTE: markdown library not supported "\n"             # TZX006
    # Replace newline characters, "\n" with <br> tags       # TZX006
    text1 = markdown_text                                   # TZX006
    text2 = text1.replace('\\n', '<br>')                    # TZX006
    html = markdown.markdown(text2)                         # TZX006

    # Parse HTML and extract text                   # TZX006
    soup = BeautifulSoup(html, 'html.parser')       # TZX006
    plain_text = soup.get_text()                    # TZX006
    
    return plain_text                               # TZX006


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


def get_all_stories():
    return db.session.query(Story).all()  # Retrieve all stories


def sort_stories(field):
    return db.session.query(Story).order_by(getattr(Story, field)).all()  # Sort based on selected field


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
        return language
    except LangDetectException as e:
        # Handle cases where detection fails
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
        

#-------------------------------------------------------------------# TZX016
# (1) When the user clicked "My Story" in the Menu, route to here.  # TZX016
#     If username exist, return to 'index.html',                    # TZX016
#     else ask the user to login.                                   # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/success')
def index():
    global EditMode                                         # TZX006

    # Ensure username exist                                 # TZX014
    try:                                                    # TZX014
        print(username)                                     # TZX014
    except NameError:                                       # TZX014
        flash("Please log in to your account.", "error")    # TZX014
        #return render_template('home.html')                # TZX014
        return redirect(url_for('logout'))                  # TZX014

    EditMode = False                                        # TZX006
    return render_template('index.html')


#-------------------------------------------------------------------# TZX016
# (1.1) If username exist, save the new story into sqlalchemy.      # TZX016
#       Then, return to 'index.html'.                               # TZX016
#-------------------------------------------------------------------# TZX016
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

    # Construct the data dictionary
    story_data = {
        "title": title,
        "content": content,
        "author": username,
        "timestamp": DateTime
    }

    #write_to_db(title, content, username, DateTime)            # TZX002
    write_to_db(story_data)                                     # TZX014

    #return redirect(url_for('index'))
    return render_template('index.html')            # TZX016


#-------------------------------------------------------------------# TZX016
# (2) When the user clicked "Story" in the Menu, route to here.     # TZX016
#     If username exist, read and get ALL story records,            # TZX016
#     then pass the records to 'storylist.html'.                    # TZX016
#     If username not exist, route to 'logout' (login required).    # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/storylist')
def storylist():

    # Ensure username exist                                 # TZX014
    try:                                                    # TZX014
        print(username)                                     # TZX014
    except NameError:                                       # TZX014
        flash("Please log in to your account.", "error")    # TZX014
        return redirect(url_for('logout'))                  # TZX014

    stories = read_from_db()                                    # TZX002

    # Store EditMode in Session                                 # TZX006
    session['EditMode'] = EditMode                              # TZX006

    # Default sort field to 'timestamp'.
    selected_field = 'timestamp'

    return render_template('storylist.html', stories=stories, editmode=EditMode, selected_field=selected_field)     # TZX016


#-------------------------------------------------------------------# TZX016
# (3) When the user clicked "Edit" in the Menu, route to here.      # TZX016
#     If username not exist, route to 'logout' (login required).    # TZX016
#     If username exist, get all stories belonging to username,     # TZX016
#     then pass these records to 'storylist.html' for display.      # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/editrecord')                                                   # TZX006
def editrecord():                                                           # TZX006

    # Retrieve username from session                                        # TZX010a
    username = session.get('username', "")  # Default to "" if not set      # TZX010a

    # Ensure username exist                                 # TZX014    
    try:                                                    # TZX014
        print(username)                                     # TZX014
    except NameError:                                       # TZX014
        flash("Please log in to your account.", "error")    # TZX014
        return redirect(url_for('logout'))                  # TZX014
                
    # Proceed if not NameError...                                   # TZX006
    EditMode = True                                                 # TZX006            
    stories = get_story_by_author(username)                         # TZX006

    # Store EditMode in Session                                     # TZX006
    session['EditMode'] = EditMode                                  # TZX006

    # Default sort field to 'timestamp'.
    selected_field = 'timestamp'

    return render_template('storylist.html', stories=stories, editmode=EditMode, selected_field=selected_field)     # TZX016


#-------------------------------------------------------------------# TZX016
# (3.1) When the user selected a story from 'storylist.html',       # TZX016
#       route to here with <timestamp> parameter.                   # TZX016
#       get a story based on <timestamp>.                           # TZX016
#       Then, return the story record to 'edit_story.html'.         # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/edit_story/<timestamp>')                               # TZX006
def edit_story(timestamp):                                          # TZX006
    global story_id                                                 # TZX016

    story = get_story_by_timestamp(timestamp)                       # TZX006
    story_id = story.id                                             # TZX016

    return render_template('edit_story.html', story=story)          # TZX006


#-------------------------------------------------------------------# TZX016
# (3.2) When user clicked 'Update' button from 'edit_story.html'.   # TZX016
#       Update the new content to the existing record.              # TZX016
#       Return to 'edit_story.html'.                                # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/update_story', methods=['POST'])                           # TZX006
def update_story():                                                     # TZX006
    
    story = Story.query.get(story_id)                                   # TZX016
    
    if story:                                                           # TZX006
        if request.method == 'POST':                                    # TZX006
            new_content = request.form['content']                       # TZX006
            story.content = new_content                                 # TZX006
            db.session.commit()                                         # TZX006

        return render_template('edit_story.html', story=story)          # TZX006
    else:                                                               # TZX006
        winsound.Beep(1000, 500)                                        # TZX016
        flash('Story not found!', 'danger')                             # TZX006
        return render_template('edit_story.html', story=story)          # TZX006


#-------------------------------------------------------------------# TZX016
# (4) When the user clicked "Admin" in the Menu, route to here.     # TZX016
#     If username not exist, route to 'logout' (login required).    # TZX016
#     If username exist, get all stories belonging to username,     # TZX016
#     then pass these records to 'archive.html' for display.        # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/archive')
def archive():

    # Ensure username exist                                 # TZX014
    try:                                                    # TZX014
        print(username)                                     # TZX014
    except NameError:                                       # TZX014
        flash("Please log in to your account.", "error")    # TZX014
        return redirect(url_for('logout'))                  # TZX014

    stories = get_story_by_author(username)                 # TZX014

    return render_template('archive.html', stories=stories)


#-------------------------------------------------------------------# TZX016
# (2.1) When the user selected a story from 'storylist.html',       # TZX016
#       route to here with <timestamp> parameter.                   # TZX016
#       get a story based on <timestamp>.                           # TZX016
#       Markdown conversion; detect language of original text,      # TZX016
#       Text-To-Speech (TTS) it, and save to 'Audio1.mp3' file.     # TZX016
#       Then, pass story record to 'story_page.html' for display.   # TZX016
#-------------------------------------------------------------------# TZX016
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
    mp3_filename = "StoryApp/static/Audio1.mp3"             # TZX013

    # Convert text to speech and save it to mp3 audio file. # TZX010
    text_to_mp3(txt, mp3_filename, language_code)           # TZX010

    # Delete Audio2.MP3 file if exist.              # TZX010
    file_path = "StoryApp/static/Audio2.mp3"        # TZX013
    if os.path.exists(file_path):                   # TZX010
        os.remove(file_path)                        # TZX010
        print(f'{file_path} has been removed.')     # TZX010
    else:                                           # TZX010
        print(f'{file_path} does not exist.')       # TZX010

    return render_template('story_page.html', story=story, data=data, languages=languages)    # TZX010


#---------------------------------------------------------------------------# TZX016
# (2.1a) When the user clicked 'Translate' button from 'story_page.html',   # TZX016
#        route to here by JavaScript (JSON)                                 # TZX016
#        Translate the original text to the required language.              # TZX016
#        Text-To-Speech (TTS) translated text and save it to 'Audio2.mp3'.  # TZX016
#        Then, return translated text to 'story_page.html' by JSON.         # TZX016
#---------------------------------------------------------------------------# TZX016
@app.route('/translate', methods=['POST'])
def translate():
    # NOTE: 'translate' library has 500 characters limitation in a single function call.
    # Work around solution: Break down large texts into smaller chunks and translate them individually. 
    # For translate non-English text, ensuring that the text is encoded in UTF-8 encoding can prevent
    # issues with character recognition and translation.
    # Here's a code to translate non-English text Using the googletrans library. 
    #

    # Delete Audio2.MP3 file if exist.              # TZX010
    file_path = "StoryApp/static/Audio2.mp3"        # TZX013
    if os.path.exists(file_path):                   # TZX010
        os.remove(file_path)                        # TZX010
        print(f'{file_path} has been removed.')     # TZX010
    else:                                           # TZX010
        print(f'{file_path} does not exist.')       # TZX010

    try:
        data = request.get_json()
        text = data.get('text')
        target_language = data.get('language')

        #TZX014# print('text:', text)

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
            mp3_filename = "StoryApp/static/Audio2.mp3"                     # TZX013

            # Convert text to speech and save it to mp3 audio file.         # TZX010
            text_to_mp3(translated_text, mp3_filename, target_language)     # TZX010
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

        return jsonify({'translation': ''.join(translated_text)})

    except Exception as e:
        return jsonify({'error': str(e)}), 400


#-------------------------------------------------------------------# TZX016
# (4.1) When user pressed "Delete" button from 'archive.html',      # TZX016
#       route to here to get 'button_value' (i.e. record timestamp) # TZX016 
#       and delete the record from database based on timestamp.     # TZX016
#       Then, return back to 'archive'.                             # TZX016
#-------------------------------------------------------------------# TZX016
@app.route('/delete_story', methods=['GET', 'POST'])
def delete_story():
    index = 0
    if request.method == "POST":
        # Get the input value from the HTML form
        record_timestamp = request.form.get('button_value')     # TZX002 added

        #TZX014# print(f'Record timestamp is {record_timestamp}')        # TZX002 changes
        
        delete_story_by_timestamp(record_timestamp)   # TZX002
        
    return redirect(url_for('archive'))


#-------------------------------------------------------------------# TZX016
# (2a) When the user needs record sorting, route to here.           # TZX016
# (3a) When the user needs record sorting, route to here.           # TZX016
#      Perform a record sorting based on user request,              # TZX016
#      then pass the sorted records to 'storylist.html'.            # TZX016
#-------------------------------------------------------------------# TZX016
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
        if selected_field not in sort_fields:
            selected_field = sort_fields[0]     # Default to first field if invalid

    # Sort records based "EditMode" (For 'View' or 'Edit' page)
    if EditMode:
        # Dynamically get the field from the Story model
        field = getattr(Story, selected_field)
        # The sorting is in ascending order by default.  # author=session.get('username')
        sorted_records = db.session.query(Story).filter_by(author=username).order_by(field).all()
    else:
        sorted_records = sort_stories(selected_field)

    return render_template('storylist.html', stories=sorted_records, editmode=EditMode, selected_field=selected_field)     # TZX016


#-------------------------------------------------------------------# TZX016
# (5) When user clicked "Leaderboard" in the Menu, route to here.   # TZX016
#     Count the total stories written by each user, and             # TZX016
#     get the top ten most productive authors records.              # TZX016
#     then pass info to 'topwriter.html' for display.               # TZX016
#-------------------------------------------------------------------# TZX016
# Top Ten Most Productive Authors / Writers
@app.route('/leaderboard')
def Leaderboard():

    # Create the subquery - get the number of story written by each author
    subquery = db.session.query(Story.author, db.func.count(Story.id).label('story_count'))\
                        .group_by(Story.author).subquery()

    # Alias the subquery for ease of use
    alias = aliased(subquery)

    # Query to get authors and their story counts, sorted by story_count in descending order and limit to top ten authors
    top_authors = db.session.query(alias.c.author, alias.c.story_count)\
                                .order_by(desc(alias.c.story_count))\
                                .limit(10).all()

    for author, story_count in top_authors:
        print(f"Author: {author}, Story Count: {story_count}")

    return render_template('topwriter.html', authors=top_authors)


def initialize_database():
    db.create_all()


@app.route('/comments', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    result = [
        {
            'id': comment.id,
            'email': comment.email,
            'comment': comment.comment,
            'author': comment.author,
            'timestamp': comment.timestamp
        }
        for comment in comments
    ]
    return jsonify(result), 200


@app.route('/comment', methods=['POST'])
def add_comment():
    data = request.json
    email = data.get('email')
    comment_text = data.get('comment')
    author = data.get('author')

    if not comment_text or not author:
        return jsonify({'error': 'Comment and author fields are required'}), 400

    new_comment = Comment(email=email, comment=comment_text, author=author)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        'id': new_comment.id,
        'email': new_comment.email,
        'comment': new_comment.comment,
        'author': new_comment.author,
        'timestamp': new_comment.timestamp
    }), 201


@app.route('/comment/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    result = {
        'id': comment.id,
        'email': comment.email,
        'comment': comment.comment,
        'author': comment.author,
        'timestamp': comment.timestamp
    }
    return jsonify(result), 200


@app.route('/comment/<int:comment_id>', methods=['PUT'])
def update_comment(comment_id):
    data = request.json
    comment = Comment.query.get_or_404(comment_id)

    comment.email = data.get('email', comment.email)
    comment.comment = data.get('comment', comment.comment)
    comment.author = data.get('author', comment.author)
    comment.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    db.session.commit()

    return jsonify({
        'id': comment.id,
        'email': comment.email,
        'comment': comment.comment,
        'author': comment.author,
        'timestamp': comment.timestamp
    }), 200


@app.route('/comment/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return jsonify(message="Comment deleted"), 204


if __name__ == '__main__':
    app.run(debug=True)
