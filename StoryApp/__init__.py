import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config["SECRET_KEY"] = "c1f15fb9b451ddfe14ae6e2baa65d787"
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['Mail_SERVER'] = 'smtp.googlemail.com'
app.config['Mail_PORT'] = 587
app.config['Mail_USE_TLS'] = True 
app.config['Mail_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['Mail_PASSWORD'] = os.environ.get('EMAIL_PASS')
mail = Mail(app)

from StoryApp import routes