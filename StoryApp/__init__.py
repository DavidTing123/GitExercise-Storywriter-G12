from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config["SECRET_KEY"] = "c1f15fb9b451ddfe14ae6e2baa65d787"
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from StoryApp import routes