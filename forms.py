from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectMultipleField, FileField
from wtforms import validators


class DatasetForm(FlaskForm):
    select = SubmitField('Select')
    datasets = SelectMultipleField('datasets', choices=[], validators=[
                                   validators.DataRequired()])

# class UploadForm(FlaskForm):
#     select = SubmitField('Select')
#     dataset = FileField('Dataset file', [validators.regexp(u'^[^/\\]\.dat$')])
