# Program name: StoryApp.py
#
# References:
#  1. HTML Form Elements
#     https://www.w3schools.com/html/html_form_elements.asp
#

from flask import Flask, render_template, request, redirect, url_for
import csv

app = Flask(__name__)

# CSV file - to store the stories data.
CSV_FILE = '.\\stories.csv'

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
    story = get_story(title)
    if story:
        return render_template('story.html', story=story)
    else:
        return "Story not found."

if __name__ == '__main__':
    app.run(debug=True)
