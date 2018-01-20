from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, SelectMultipleField, FileField, DecimalField, RadioField, FloatField
from wtforms import validators


class DatasetForm(FlaskForm):
    select = SubmitField('Plot Data')
    datasets = SelectMultipleField('datasets', choices=[], validators=[
                                   validators.DataRequired()])

class UploadForm(FlaskForm):
    data_file = FileField('dataset', validators=[
        FileRequired(),
        FileAllowed(['dat'], 'datasets only!')
    ])
    radio_inputType = RadioField(u'Data Type', choices=[('DD', 'DD [m_DM,sigma]'), ('LHC', 'LHC [m_med,m_DM]')])
    upload_button = SubmitField('Upload Dataset')

class Set_gSM_Form(FlaskForm):
    gD_input = FloatField('gD_input')
    gU_input = FloatField('gU_input')
    gS_input = FloatField('gS_input')
    set_button = SubmitField('Refresh Plot')
