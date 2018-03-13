# -*- coding: utf-8 -*-
import os
from itertools import cycle
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.models import LinearAxis, Label
import bokeh
import pandas as pd
from flask import send_from_directory
import numpy as np

from plotter import get_figure, get_data, get_datasets, get_metadata, DATA_LOCATION, set_gSM, get_gSM, set_SI_modifier, get_SI_modifier
from forms import DatasetForm, UploadForm, Set_gSM_Form

ALLOWED_EXTENSIONS = set(['xml'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DATA_LOCATION
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 's3cr3t'

#Default
selected_datasets = ['LUX_2016_SI', 'CMS_monojet_July2017_VECTOR']

JS_CODE = """
import {Label, LabelView} from "models/annotations/label"

export class LatexLabelView extends LabelView
  render: () ->

    #--- Start of copied section from ``Label.render`` implementation

    # Here because AngleSpec does units tranform and label doesn't support specs
    switch @model.angle_units
      when "rad" then angle = -1 * @model.angle
      when "deg" then angle = -1 * @model.angle * Math.PI/180.0

    panel = @model.panel ? @plot_view.frame

    xscale = @plot_view.frame.xscales[@model.x_range_name]
    yscale = @plot_view.frame.yscales[@model.y_range_name]

    sx = if @model.x_units == "data" then xscale.compute(@model.x) else panel.xview.compute(@model.x)
    sy = if @model.y_units == "data" then yscale.compute(@model.y) else panel.yview.compute(@model.y)

    sx += @model.x_offset
    sy -= @model.y_offset

    #--- End of copied section from ``Label.render`` implementation

    # Must render as superpositioned div (not on canvas) so that KaTex
    # css can properly style the text
    @_css_text(@plot_view.canvas_view.ctx, "", sx, sy, angle)

    # ``katex`` is loaded into the global window at runtime
    # katex.renderToString returns a html ``span`` element
    katex.render(@model.text, @el, {displayMode: true})

export class LatexLabel extends Label
  type: 'LatexLabel'
  default_view: LatexLabelView
"""
class LatexLabel(Label):
    """A subclass of the Bokeh built-in `Label` that supports rendering
    LaTex using the KaTex typesetting library.

    Only the render method of LabelView is overloaded to perform the
    text -> latex (via katex) conversion. Note: ``render_mode="canvas``
    isn't supported and certain DOM manipulation happens in the Label
    superclass implementation that requires explicitly setting
    `render_mode='css'`).
    """
    __javascript__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.js"]
    __css__ = ["https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.6.0/katex.min.css"]
    __implementation__ = JS_CODE


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def main():
    return redirect('/index')

@app.route('/updateValues', methods=['GET', 'POST'])
def updateValues():
    gSM_refresh = Set_gSM_Form()
    gSM = gSM_refresh.gSM_input.data
    set_gSM(gSM,gSM,gSM)
    #Future: Individually set coupling constant
    #gU = gSM_refresh.gU_input.data
    #gD = gSM_refresh.gD_input.data
    #gS = gSM_refresh.gS_input.data
    #set_gSM(gU,gD,gS)
    return redirect(url_for('index'))

@app.route('/index', methods=['GET', 'POST'])
def index():
    known_datasets = get_datasets()
    gu, gd, gs = get_gSM()
    si_modifier = get_SI_modifier()

    dataset_selection = DatasetForm(gSM_input=gu)
    dataset_selection.datasets.choices = zip(get_datasets(), get_datasets())
    dataset_upload = UploadForm()

    global selected_datasets

    if request.method == 'POST':
        # check if the post request has the file part
        # print(request.values, request.data, request.form)
        print(dataset_selection.datasets.data)
        if dataset_selection.validate():
            selected_datasets = dataset_selection.datasets.data
            gSM = dataset_selection.gSM_input.data
            set_gSM(gSM,gSM,gSM)
            gu, gd, gs = get_gSM()
            si_modifier = dataset_selection.radio_inputSI.data
            set_SI_modifier(si_modifier)

    datasets = selected_datasets
    dfs = map(get_data, datasets)
    metadata = map(get_metadata, datasets)
    metadata2 = map(get_metadata, datasets)
    allmetadata = map (get_metadata,known_datasets)
    colors = cycle(['red', 'blue', 'green', 'orange'])

    p1 = figure(
        title='DD Results',
        tools='wheel_zoom, pan, save',
        x_axis_label='mMed',
        x_axis_type="log",
        y_axis_label="mDM",
        y_axis_type="log",
        plot_width=500,
        plot_height=500,
    )
    p1.title.text_font_size = "1.2em"
    p1.xaxis.axis_label_text_font_size = "14pt"
    p1.yaxis.axis_label_text_font_size = "14pt"

    '''
    x = np.arange(0.0, 1.0 + 0.01, 0.01)
    y = np.cos(2*2*np.pi*x) + 2

    p1 = figure(title="LaTex Demonstration", plot_width=500, plot_height=500)
    p1.line(x, y)
    latex = LatexLabel(text="f = \sum_{n=1}^\infty\\frac{-e^{i\pi}}{2^n}!",
                        x=35, y=445, x_units='screen', y_units='screen',
                        render_mode='css', text_font_size='16pt',
                        background_fill_color='#ffffff')

    p1.add_layout(latex)
    '''
    p2 = figure(
        title='Collider Conversion',
        tools='wheel_zoom, pan, save',
        x_axis_label='mDM',
        x_axis_type="log",
        #y_axis_label="$\sigma_{DM}$ (cross-section)",
        y_axis_label="σDM (cross-section)",
        y_axis_type="log",
        plot_width=500,
        plot_height=500,
    )
    p2.title.text_font_size = "1.2em"
    p2.xaxis.axis_label_text_font_size = "14pt"
    p2.yaxis.axis_label_text_font_size = "14pt"

    for df, color in zip(dfs, colors):
        label = df['label'].any()
        p1.line(df['m_med'], df['m_DM'], line_width=2, color=color, legend=label)
        p2.line(df['m_DM'], df['sigma'], line_width=2, color=color, legend=label)
        '''
        if(df['type'].any()=='DD'):
            p1.line(df['m_med'], df['m_DM'], line_width=2, color=color, legend=label)
        elif(df['type'].any()=='LHC'):
            p2.line(df['m_DM'], df['sigma'], line_width=2, color=color, legend=label)
        '''

    all_data = pd.concat(dfs)

    script1, div1 = components(p1, CDN)
    script2, div2 = components(p2, CDN)
    return render_template('index.html',
                           plot_script1=script1, plot_div1=div1,
                           plot_script2=script2, plot_div2=div2,
                           bokeh_version=bokeh.__version__,
                           data_table=all_data.to_html(),
                           datasets = known_datasets,
                           metadata = metadata,
                           dataset_selection = dataset_selection,
                           selected_datasets = selected_datasets,
                           allmetadata = allmetadata,
                           dataset_upload = dataset_upload,
                           si_modifier = si_modifier,
                           gSM_gSM=gu,
                           gSM_gU=gu,gSM_gD=gd,gSM_gS=gs)

@app.route('/pdf', methods=['GET', 'POST'])
def pdf():
    gu, gd, gs = get_gSM()

    global selected_datasets
    #Will re-use the previously selected values for the dataset
    #Optional: provide dataset files in the post parameters
    if request.method == 'POST':
        print('Use this area to parse for posted datasets');

    datasets = selected_datasets

    dfs = map(get_data, datasets)
    metadata = map(get_metadata, datasets)

    colors = cycle(['red', 'blue', 'green', 'orange'])
    p = figure(
        title='DD2LHC Pico (p, axial)',
        tools='wheel_zoom, pan, save',
        x_axis_label='m_DM',
        x_axis_type="log",
        y_axis_label='sigma',
        y_axis_type="log",
        plot_width=600,
        plot_height=600,
    )

    for df, color in zip(dfs, colors):
        p.line(df['m_DM'], df['sigma'], line_width=2,
               color=color, legend=df['label'][0])

    all_data = pd.concat(dfs)

    script, div = components(p, CDN)
    #ToDo: Turn this render_template into a PDF file and download
    return render_template('pdf.html',
                           plot_script1=script1, plot_div1=div1,
                           plot_script2=script2, plot_div2=div2,
                           bokeh_version=bokeh.__version__,
                           data_table=all_data.to_html(),
                           metadata = metadata,
                           gSM_gSM=gu)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        f = form.data_file.data
        filename = secure_filename(f.filename)
        t = form.radio_inputType.data
        session[filename] = t
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename
        ))
    return redirect(url_for('index'))

if __name__ == '__main__':
    #test_figure()
    app.run(port=5000)
