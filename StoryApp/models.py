from flask import current_app
from itsdangerous import URLSafeTimedSerializer 
from StoryApp import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id =db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(25),unique=True, nullable=False)
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")

    def get_reset_token(self):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}).encode('utf-8')
    
    @staticmethod
    def verify_reset_token(token):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'], )
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}, '{self.email}' ,'{self.image_file}')"


# Define a "Story" model with columns for title and content.            # TZX002
class Story(db.Model):                                                  # TZX002
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)    # TZX002
    title = db.Column(db.String(50))                                    # TZX002
    content = db.Column(db.String(500))                                 # TZX002
    # Use username as an author name.                                   # TZX002
    author = db.Column(db.String(20), nullable=False)                   # TZX002
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
