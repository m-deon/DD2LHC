from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, SelectMultipleField, FileField, DecimalField, RadioField, FloatField, SelectField
from wtforms import validators


class DatasetForm(FlaskForm):
    select = SubmitField('Plot Data')
    gSM_input = FloatField('gSM_input')
    conditional_input = RadioField(u'Data Type', choices=[(u'SD', 'Spin-Dependent'), (u'SI', 'Spin-Independent')], validators=[validators.Optional()])
    radio_inputSI = RadioField(u'Spin-Independent', choices=[('scalar', 'Scalar'), ('vector', 'Vector')], default='scalar',validators=[validators.Optional()])
    datasets = SelectMultipleField('datasets', choices=[], validators=[validators.DataRequired()])
    savedPlots = SelectField('datasets', choices=[], validators=[validators.Optional()])
    #gSM_input = FloatField('gSM_input')
    #conditional_input = RadioField(u'Conditional Type', choices=[('SD', 'Spin-Dependent'), ('SI', 'Spin-Independent')])

class UploadForm(FlaskForm):
    data_file = FileField('dataset', validators=[
        FileRequired(),
        FileAllowed(['xml'], 'datasets only!')
    ])
    upload_button = SubmitField('Upload Dataset')

class Set_gSM_Form(FlaskForm):
    #gSM_input = FloatField('gSM_input')
    gD_input = FloatField('gD_input')
    gU_input = FloatField('gU_input')
    gS_input = FloatField('gS_input')
    set_button = SubmitField('Refresh Plot')
