from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from StoryApp.models import User

class SignUpForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Sign Up")

    def validate_email(self, email):

        email = email.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already signed up. Please signed up with another email.')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('This username is taken. Please choose another one.')

class LogInForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=5, max=20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Log In")