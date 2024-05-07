from app import SignUpForm, LogInForm
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class SignUpForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Sign Up")

class LogInForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    remember =BooleanField("Remember Me")
    submit = SubmitField("Log In")