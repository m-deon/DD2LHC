import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import bokeh
import pandas as pd
from flask import send_from_directory

from plotter import get_figure, get_data

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'dat'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return redirect('/index')


@app.route('/index')
def index():
    plot = figure()
    plot.circle([1, 2], [3, 4])

    script, div = components(plot, CDN)

    p = figure(plot_width=400, plot_height=400)

    # add a square renderer with a size, color, and alpha
    # p.square([1, 2, 3, 4, 5], [6, 7, 2, 4, 5], size=20, color="olive", alpha=0.5)

    df = get_data('data/PICOSD_p.dat')
    df2 = get_data('data/LHC_2_DD_n.dat')
    df3 = get_data('data/DD_2_LHC_p.dat')
    p = figure(plot_width=400, plot_height=400, y_axis_type="log",
               title='DD2LHC Pico (p, axial)', x_axis_label='m_med',
               y_axis_label='m_DM')
    p.line(df['m_med'], df['m_DM'], line_width=2,
           color='red', legend=df['label'][0])
    p.line(df2['m_med'], df2['m_DM'], line_width=2,
           color='blue', legend=df2['label'][0])
    p.line(df3['m_med'], df3['m_DM'], line_width=2,
           color='green', legend=df3['label'][0])

    all_data = pd.concat([df, df2, df3])
    # fig = get_figure(df)
    # p = mpl.to_bokeh(fig)

    script, div = components(p, CDN)
    return render_template('index.html', script=script, the_div=div, bokeh_version=bokeh.__version__, table=all_data.to_html())

# improve with
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

if __name__ == '__main__':
    app.run(port=5000)
