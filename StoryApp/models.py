from StoryApp import db
from StoryApp import db, login_manager

class User(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(25),unique=True, nullable=False)
    username = db.Column(db.String(20),unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")

    def __repr__(self):
        return f"User('{self.username}, '{self.email}' ,'{self.image_file}')"
