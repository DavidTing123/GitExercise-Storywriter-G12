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
#

from flask import Flask, render_template, request, redirect, url_for
import csv
import pyttsx3   # a simple text-to-speech converter library in Python

app = Flask(__name__)

# CSV file - to store the stories data.
#CSV_FILE = 'C:\\Users\\tingk\\OneDrive\\Documents\\GitHub\\DavidTing123-GitExercise-GroupTT1L-12\\stories.csv'
CSV_FILE = '.\\stories.csv'
#CSV_FILE = 'C:\\Users\\tingk\\OneDrive\\Desktop\\TKL\\Python\\Project\\StoryWriter\\stories.csv'

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
