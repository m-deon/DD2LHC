# -*- coding: utf-8 -*-
import os
from flask import Blueprint, redirect, render_template
from flask import request, url_for
from flask_user import current_user, login_required, roles_required

from app import db
from app import app
from app.models.user_models import UserProfileForm

#DM Limiter
from itertools import cycle
from flask import Flask, render_template, request, redirect, url_for, session, json, make_response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import CombinedMultiDict
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.models import LinearAxis, Label, Legend
import bokeh
import pandas as pd
from flask import send_from_directory
import numpy as np
#import pdfkit
#DM Packages
from app.dmplotter.plotter import get_data, get_datasets, get_metadata, set_SI_modifier, get_SI_modifier, getSimplifiedPlot, getDDPlot, getLegendPlot
from app.dmplotter.forms import DatasetForm, UploadForm, Set_gSM_Form
from app.dmplotter.conversion import set_gSM, get_gSM
#DM Default
ALLOWED_EXTENSIONS = set(['xml'])
selected_datasets = []
colors = cycle(['red', 'blue', 'green', 'orange'])
savedPlots = json.load(open("savedPlots.json"))
def determine(data):
    if data is None:
        return False;
    else:
        return True;

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getSavedPlots():
    plots = savedPlots
    return plots
#End DM

main_blueprint = Blueprint('main', __name__, template_folder='templates')

# The Home page is accessible to anyone
@main_blueprint.route('/')
def home_page():
    return render_template('main/home_page.html')


# The User page is accessible to authenticated users (users that have logged in)
@main_blueprint.route('/member')
@login_required  # Limits access to authenticated users
def member_page():
    return render_template('main/user_page.html')


# The Admin page is accessible to users with the 'admin' role
@main_blueprint.route('/admin')
@roles_required('admin')  # Limits access to users with the 'admin' role
def admin_page():
    return render_template('main/admin_page.html')


@main_blueprint.route('/main/profile', methods=['GET', 'POST'])
@login_required
def user_profile_page():
    # Initialize form
    form = UserProfileForm(request.form, obj=current_user)

    # Process valid POST
    if request.method == 'POST' and form.validate():
        # Copy form fields to user_profile fields
        form.populate_obj(current_user)

        # Save user_profile
        db.session.commit()

        # Redirect to home page
        return redirect(url_for('main.home_page'))

    # Process GET or invalid POST
    return render_template('main/user_profile_page.html',
                           form=form)

@main_blueprint.route('/about')
def about_page():
    return render_template('about.html')

@main_blueprint.route('/theory')
def theory_page():
    return render_template('theory.html')

@main_blueprint.route('/dmplotter', methods=['GET', 'POST'])
@login_required
def dmplotter():
    known_datasets = get_datasets()
    gu, gd, gs = get_gSM()
    si_modifier = get_SI_modifier()

    #Generate Array of options
    options = list(getSavedPlots().keys())

    dataset_selection = DatasetForm(gSM_input=gu)
    dataset_selection.datasets.choices = zip(get_datasets(), get_datasets())
    dataset_selection.savedPlots.choices = zip(options, options)
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

    #Filter, TODO: Apply filter to selected_datasets prior to conversion (attempt)
    #get_data will return a 'None' object if the selected dataset could not be converted, (bad experiement string..)
    dfs = [x for x in dfs if determine(x)]

    metadata = map(get_metadata, datasets)
    allmetadata = map (get_metadata,known_datasets)

    p1 = getSimplifiedPlot()
    p2 = getDDPlot()
    legendPlot = getLegendPlot()

    legendItems = []
    x = 1
    y = 2*x
    for df, color in zip(dfs, colors):
        label = df['label'].any()
        df['color'] = color
        p1.line(df['m_med'], df['m_DM'], line_width=2, color=color)
        p2.line(df['m_DM'], df['sigma'], line_width=2, color=color)
        line = legendPlot.line(x,y,line_width=2, color=color)
        legendItems.append((label,[line]))

    #Initialize all_data in the case that all datasets selected where invalid
    all_data = pd.DataFrame()
    if(len(dfs) > 0):
        all_data = pd.concat(dfs)

    legend = Legend(items=legendItems, location=(0, 0))
    legendPlot.add_layout(legend, 'above')

    script1, div1 = components(p1, CDN)
    script2, div2 = components(p2, CDN)
    script3, div3 = components(legendPlot,CDN)
    return render_template('dmplotter.html',
                           plot_script1=script1, plot_div1=div1,
                           plot_script2=script2, plot_div2=div2,
                           plot_script3=script3, plot_div3=div3,
                           bokeh_version=bokeh.__version__,
                           data_table=all_data.to_html(),
                           datasets = known_datasets,
                           metadata = metadata,
                           dataset_selection = dataset_selection,
                           selected_datasets = selected_datasets,
                           allmetadata = allmetadata,
                           savedPlots = getSavedPlots(),
                           dataset_upload = dataset_upload,
                           si_modifier = si_modifier,
                           gSM_gSM=gu,
                           gSM_gU=gu,gSM_gD=gd,gSM_gS=gs)

@main_blueprint.route('/updateValues', methods=['GET', 'POST'])
def updateValues():
    gSM_refresh = Set_gSM_Form()
    gSM = gSM_refresh.gSM_input.data
    set_gSM(gSM,gSM,gSM)
    #Future: Individually set coupling constant
    #gU = gSM_refresh.gU_input.data
    #gD = gSM_refresh.gD_input.data
    #gS = gSM_refresh.gS_input.data
    #set_gSM(gU,gD,gS)
    return redirect(url_for('main.dmplotter'))

@main_blueprint.route('/savePlot', methods=['GET', 'POST'])
def savePlot():
    global savedPlots

    savedPlotName = request.form['name']
    selected_datasets = request.form['data'].split(",")

    #Save to local copy and then flush to disk
    savedPlots[savedPlotName] = selected_datasets
    with open('savedPlots.json', 'w') as f:
        json.dump(savedPlots, f)
    return redirect(url_for('main.dmplotter'))

@main_blueprint.route('/pdf', methods=['GET', 'POST'])
def generatePDF():

    gu, gd, gs = get_gSM()
    si_modifier = get_SI_modifier()

    global selected_datasets
    #Will re-use the previously selected values for the dataset_type
    #Optional: provide datasel file names in the POST parameters
    if request.method == 'POST':
        print('Use this are to parse to posted datasets');

    datasets = selected_datasets
    dfs = map(get_data, datasets)

    #Filter, TODO: Apply filter to selected_datasets prior to conversion (attempt)
    #get_data will return a 'None' object if the selected dataset could not be converted, (bad experiement string..)
    dfs = [x for x in dfs if determine(x)]

    metadata = map(get_metadata, datasets)

    p1 = getSimplifiedPlot()
    p2 = getDDPlot()
    legendPlot = getLegendPlot()

    legendItems = []
    x = 1
    y = 2*x
    for df, color in zip(dfs, colors):
        label = df['label'].any()
        df['color'] = color
        p1.line(df['m_med'], df['m_DM'], line_width=2, color=color)
        p2.line(df['m_DM'], df['sigma'], line_width=2, color=color)
        line = legendPlot.line(x,y,line_width=2, color=color)
        legendItems.append((label,[line]))

    #Initialize all_data in the case that all datasets selected where invalid
    all_data = pd.DataFrame()
    if(len(dfs) > 0):
        all_data = pd.concat(dfs)

    legend = Legend(items=legendItems, location=(0, 0))
    legendPlot.add_layout(legend, 'above')

    script1, div1 = components(p1, CDN)
    script2, div2 = components(p2, CDN)
    script3, div3 = components(legendPlot,CDN)
    html =  render_template('pdf.html',
                           plot_script1=script1, plot_div1=div1,
                           plot_script2=script2, plot_div2=div2,
                           plot_script3=script3, plot_div3=div3,
                           bokeh_version=bokeh.__version__,
                           metadata = metadata,
                           selected_datasets = selected_datasets,
                           si_modifier = si_modifier,
                           gSM_gSM=gu)
    return html
'''
    css = 'app/static/css/style.css'
    pdf = pdfkit.from_string(html, False, css=css)

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = \
                    'inline; filename=%s.pdf' % 'dd2lhc'
    return response
'''

@main_blueprint.route('/upload', methods=['GET', 'POST'])
def upload():
    form = UploadForm(CombinedMultiDict((request.files, request.form)))
    if form.validate_on_submit():
        f = form.data_file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('main.dmplotter'))
