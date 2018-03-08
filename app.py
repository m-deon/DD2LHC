import os
from itertools import cycle
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import bokeh
import pandas as pd
from flask import send_from_directory

from plotter import get_figure, get_data, get_datasets, get_metadata, DATA_LOCATION, set_gSM, get_gSM, set_SI_modifier, get_SI_modifier
from forms import DatasetForm, UploadForm, Set_gSM_Form

ALLOWED_EXTENSIONS = set(['xml'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = DATA_LOCATION
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = 's3cr3t'

#Default
selected_datasets = ['LUX_2016_SI', 'CMS_monojet_July2017_VECTOR']

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
    allmetadata = map (get_metadata,known_datasets)
    colors = cycle(['red', 'blue', 'green', 'orange'])

    p = figure(
        title='Dark Matter Limiter Conversion Plot',
        tools='wheel_zoom, pan, save',
        x_axis_label='m_DM',
        x_axis_type="log",
        #y_axis_label="$\sigma_{DM}$ (cross-section)",
        y_axis_label="sigma_DM (cross-section)",
        y_axis_type="log",
        plot_width=600,
        plot_height=600,
    )

    for df, color in zip(dfs, colors):
        label = df['label'][0]
        #Appending the extrapolated data (lhc), messes with the dataframe and underlying types
        #Not sure why, need to futher investigate.
        if(isinstance(label,pd.Series)):
            label = label.values[0]

        #p.line(df['m_med'], df['m_DM'], line_width=2,
        p.line(df['m_DM'], df['sigma'], line_width=2,
               color=color, legend=label)

    all_data = pd.concat(dfs)

    script, div = components(p, CDN)
    return render_template('index.html', plot_script=script, plot_div=div,
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
    return render_template('pdf.html', plot_script=script, plot_div=div,
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
