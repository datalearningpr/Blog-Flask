
from flask_wtf import FlaskForm, validators

from wtforms import TextField, PasswordField, TextAreaField, HiddenField, StringField
from wtforms.validators import Required, EqualTo, ValidationError

from Blog.models import User


class LoginForm(FlaskForm):
    username = TextField("username", validators=[Required()])
    password = PasswordField("password", validators=[Required()])

# define customized validator to use unique username
def validate_username(self, field):
    if User.query.filter_by(username=field.data).first():
        raise ValidationError('name taken')

class RegisterForm(FlaskForm):
    username = TextField("username", validators=[Required(), validate_username])
    password = PasswordField("password", validators=[Required(), EqualTo("confirm", message='Passwords must match')])
    confirm = PasswordField("repeat password")
