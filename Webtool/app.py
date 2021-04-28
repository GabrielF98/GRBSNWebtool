from flask import Flask, render_template
from werkzeug.exceptions import abort

#Find the txt files with the right names
import glob
import numpy as np

#Pieces for Bokeh
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from flask import Flask, request, render_template, abort, Response
from bokeh.plotting import figure
from bokeh.embed import components


#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(event_id):
    conn = get_db_connection()
    event = conn.execute('SELECT * FROM SQLDataGRBSNe WHERE GRB = ?',
                        (event_id,)).fetchall()
    conn.close()
    if event is None:
        abort(404)
    return event

def grb_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT(GRB) FROM SQLDataGRBSNe')
    grbs = []
    for i in names:
    	grbs.append(i[0])
    conn.close()
    
    return grbs

#This code goes to the long_grbs folder and gets all the data for the plot
def get_grb_data(event_id):
    path = './static/long_grbs/'
    files = glob.glob(path+'/*.txt')
    print(files)

    for i in range(len(files)):
        if str(event_id) in str(files[i]):
            k = np.loadtxt(files[i], skiprows=1, unpack=True)
            break
        else:
            k = [[0], [0], [0], [0], [0], [0]]
    return(k)

def bokeh_plot(data):
    t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg = data

    # create a new plot with a title and axis labels
    plot = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")

    # add a line renderer with legend and line thickness
    plot.scatter(t, flux, legend_label="GRB", line_width=2)
    

    return(p)


app = Flask(__name__)

#The pages we want
#The homepage and its location
@app.route('/')
def home():
    return render_template('home.html')

#Be able to select the GRBs by their names and go
#To a specific page
@app.route('/<event_id>')
def event(event_id):
    source = ColumnDataSource()
    event = get_post(event_id)
    data = get_grb_data(event_id)

    t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg = data
    # create a new plot with a title and axis labels

    plot = figure(plot_width=900, plot_height=500,title=None, toolbar_location="right", y_axis_type="log", x_axis_type="log")

    # add a line renderer with legend and line thickness
    plot.scatter(t, flux, legend_label="Swift/XRT", line_width=2)
    plot.xaxis.axis_label = 'Time [sec]'
    plot.yaxis.axis_label = 'Flux (0.3-10keV) [erg/cm^2/sec]'

    script, div = components(plot)
    kwargs = {'script': script, 'div': div}
    kwargs['title'] = 'bokeh-with-flask'
    return render_template('event.html', event=event, **kwargs)

@app.route('/docs')
def docs():
    return render_template('docs.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')

#Enable a table on the homepage with links to GRB pages
# @app.route('/<event_id>')
# def event(event_id):
#     event = get_post(event_id)

#     #Links
#     return redirect(url_for('index'))
#     return render_template('event.html', event=event)

# @app.route('/names/')
# def names():
# 	names = grb_names()
# 	return render_template('names.html', names=names)

if __name__ == "__main__":
    #debug=True lets you do it without rerunning all the time

    app.run(debug = True)