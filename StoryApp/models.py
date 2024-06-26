from flask import current_app
from StoryApp import db, login_manager, app
from flask_login import UserMixin
from datetime import datetime 

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id =db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(25),unique=True, nullable=False)
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    bio = db.Column(db.Text)

def __repr__(self):
        return f"User('{self.username}, '{self.email}' ,'{self.image_file}')"


# Define a "Story" model with columns for title and content.            # TZX002
class Story(db.Model):                                                  # TZX002
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # TZX002
    title = db.Column(db.String(50))                                    # TZX002
    content = db.Column(db.String(1000))                                # TZX006
    # Use username as an author name.                                   # TZX002
    author = db.Column(db.String(50), nullable=False)                   # TZX006
    # To deal with multiple stories that share the same title,          # TZX002
    # I decided to use the creation timestamp as an unique key          # TZX002
    # to retrieve (and to delete) the story record.                     # TZX002 
    timestamp = db.Column(db.String(19))                                # TZX002

def __init__(self, id, title, content, author, timestamp):      # TZX002
    self.id = id                                                # TZX002
    self.title = title                                          # TZX002
    self.content = content                                      # TZX002
    self.author = author                                        # TZX002
    self.timestamp = timestamp                                  # TZX002

# TZX011 (start) ----------------------------------------------------------------
# Commented 'Rating' table. 
'''
class Rating(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('story.id'), nullable=False)
#    story_timestamp = db.Column(db.String(19), nullable=False)     # TZX013
    rating = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), nullable=False)
'''
# TZX011 (end) ----------------------------------------------------------------

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(50), nullable=True)
    comment = db.Column(db.String(1000), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.String(19), nullable=False, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def __init__(self, email, comment, author, timestamp=None):
        self.email = email
        self.comment = comment
        self.author = author
        self.timestamp = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def initialize_database():
    db.create_all()

if __name__ == '__main__':
    from StoryApp import app  # Ensure to import your Flask app instance here
    with app.app_context():
        initialize_database()

if __name__ == '__main__':
    with app.app_context():
        initialize_database()
