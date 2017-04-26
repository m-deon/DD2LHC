from flask import Flask, render_template, request, redirect
from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import components
import bokeh
import pandas as pd

from plotter import get_figure, get_data


app = Flask(__name__)


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

if __name__ == '__main__':
    app.run(port=5000)
