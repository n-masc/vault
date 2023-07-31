from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError
from models import User


class RegisterForm(FlaskForm):
    def validate_username(self, username_to_check):
        user = User.query.filter_by(username=username_to_check.data).first()
        if user:
            raise ValidationError("Username already in use. Please try another username")

    def validate_email(self, email_to_check):
        email = User.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError("Email address already in use. Please enter another email address")

    username = StringField("Username:", validators=[DataRequired()])
    email = StringField("Email address:", validators=[Email(), DataRequired()])
    password1 = PasswordField("Password:", validators=[Length(min=8), DataRequired()])
    password2 = PasswordField("Confirm password:", validators=[EqualTo('password1'), DataRequired()])
    submit = SubmitField('Register new user')


class LoginForm(FlaskForm):
    username = StringField("Username:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    submit = SubmitField('Login user')


class RateGameForm(FlaskForm):
    graphics = IntegerField('Graphics: /10', validators=[DataRequired()])
    soundtrack = IntegerField('Soundtrack: /10', validators=[DataRequired()])
    gameplay = IntegerField('Gameplay: /10', validators=[DataRequired()])
    story = IntegerField('Story: /10', validators=[DataRequired()])
    submit = SubmitField("Add Ratings")
