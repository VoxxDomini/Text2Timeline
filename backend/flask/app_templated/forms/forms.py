from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, Optional

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class TextOrFileForm(FlaskForm):
    text_area = TextAreaField('Text', validators=[Optional()])
    file_upload = FileField('Upload File', validators=[Optional()])
    parser_selection = SelectField("Select a parser", choices=[])
    submit = SubmitField('Submit')