from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, SelectMultipleField, FileField
from wtforms import validators


class DatasetForm(FlaskForm):
    select = SubmitField('Select')
    datasets = SelectMultipleField('datasets', choices=[], validators=[
                                   validators.DataRequired()])

class UploadForm(FlaskForm):
    data_file = FileField('dataset', validators=[
        FileRequired(),
        FileAllowed(['dat'], 'datasets only!')
    ])
    upload_button = SubmitField('Upload')
