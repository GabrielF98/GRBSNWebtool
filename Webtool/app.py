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
from bokeh.layouts import gridplot
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
grbs = grb_names()

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

# def bokeh_plot(data):
#     t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg = data

#     # create a new plot with a title and axis labels
#     plot = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")

#     # add a line renderer with legend and line thickness
#     plot.scatter(t, flux, legend_label="GRB", size=200)
    

#     return(p)


app = Flask(__name__)
app.secret_key = 'secretKey'

#The pages we want
#The homepage and its location
@app.route('/')
def home():
    return render_template('home.html')

#Be able to select the GRBs by their names and go
#To a specific page, it also plots the XRT data

@app.route('/<event_id>')
def event(event_id):
    source = ColumnDataSource()
    event = get_post(event_id)
    data = get_grb_data(event_id)

    t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg = data
    # create a new plot with a title and axis labels

    plot = figure(plot_width=900, plot_height=500,title=None, toolbar_location="right", y_axis_type="log", x_axis_type="log")
    
    # add a line renderer with legend and line thickness
    plot.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

    #Aesthetics
    #Axis font size
    plot.yaxis.axis_label_text_font_size = '16pt'
    plot.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    plot.xaxis.axis_label_text_color = 'white'
    plot.xaxis.major_label_text_color = 'white'

    plot.yaxis.axis_label_text_color = 'white'
    plot.yaxis.major_label_text_color = 'white'

    #Tick colors 
    plot.xaxis.major_tick_line_color = 'white'
    plot.yaxis.major_tick_line_color = 'white'

    plot.xaxis.minor_tick_line_color = 'white'
    plot.yaxis.minor_tick_line_color = 'white'

    #Axis labels
    plot.xaxis.axis_label = 'Time [sec]'
    plot.yaxis.axis_label = 'Flux (0.3-10keV) [erg/cm^2/sec]'

    #Axis Colors
    plot.xaxis.axis_line_color = 'white'
    plot.yaxis.axis_line_color = 'white'

    #Make ticks larger
    plot.xaxis.major_label_text_font_size = '16pt'
    plot.yaxis.major_label_text_font_size = '16pt'

    plot.background_fill_color = 'teal'
    plot.border_fill_color = 'teal'



    #script, div = components(plot)
    

    optical = figure(title=None, toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness
    optical.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

        #Aesthetics
    #Axis font size
    optical.yaxis.axis_label_text_font_size = '16pt'
    optical.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    optical.xaxis.axis_label_text_color = 'white'
    optical.xaxis.major_label_text_color = 'white'

    optical.yaxis.axis_label_text_color = 'white'
    optical.yaxis.major_label_text_color = 'white'

    #Tick colors 
    optical.xaxis.major_tick_line_color = 'white'
    optical.yaxis.major_tick_line_color = 'white'

    optical.xaxis.minor_tick_line_color = 'white'
    optical.yaxis.minor_tick_line_color = 'white'

    #Axis labels
    optical.xaxis.axis_label = 'Time [sec]'
    optical.yaxis.axis_label = 'Flux (0.3-10keV) [erg/cm^2/sec]'

    #Axis Colors
    optical.xaxis.axis_line_color = 'white'
    optical.yaxis.axis_line_color = 'white'

    #Make ticks larger
    optical.xaxis.major_label_text_font_size = '16pt'
    optical.yaxis.major_label_text_font_size = '16pt'

    optical.background_fill_color = 'teal'
    optical.border_fill_color = 'teal'


    radio = figure(title=None, toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness
    radio.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

    #Aesthetics
    #Axis font size
    radio.yaxis.axis_label_text_font_size = '16pt'
    radio.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    radio.xaxis.axis_label_text_color = 'white'
    radio.xaxis.major_label_text_color = 'white'

    radio.yaxis.axis_label_text_color = 'white'
    radio.yaxis.major_label_text_color = 'white'

    #Tick colors 
    radio.xaxis.major_tick_line_color = 'white'
    radio.yaxis.major_tick_line_color = 'white'

    radio.xaxis.minor_tick_line_color = 'white'
    radio.yaxis.minor_tick_line_color = 'white'

    #Axis labels
    radio.xaxis.axis_label = 'Time [sec]'
    radio.yaxis.axis_label = 'Flux (0.3-10keV) [erg/cm^2/sec]'

    #Axis Colors
    radio.xaxis.axis_line_color = 'white'
    radio.yaxis.axis_line_color = 'white'

    #Make ticks larger
    radio.xaxis.major_label_text_font_size = '16pt'
    radio.yaxis.major_label_text_font_size = '16pt'

    radio.background_fill_color = 'teal'
    radio.border_fill_color = 'teal'


    spectrum = figure(title=None, toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness
    spectrum.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')
        #Aesthetics
    #Axis font size
    spectrum.yaxis.axis_label_text_font_size = '16pt'
    spectrum.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    spectrum.xaxis.axis_label_text_color = 'white'
    spectrum.xaxis.major_label_text_color = 'white'

    spectrum.yaxis.axis_label_text_color = 'white'
    spectrum.yaxis.major_label_text_color = 'white'

    #Tick colors 
    spectrum.xaxis.major_tick_line_color = 'white'
    spectrum.yaxis.major_tick_line_color = 'white'

    spectrum.xaxis.minor_tick_line_color = 'white'
    spectrum.yaxis.minor_tick_line_color = 'white'

    #Axis labels
    spectrum.xaxis.axis_label = 'Time [sec]'
    spectrum.yaxis.axis_label = 'Flux (0.3-10keV) [erg/cm^2/sec]'

    #Axis Colors
    spectrum.xaxis.axis_line_color = 'white'
    spectrum.yaxis.axis_line_color = 'white'

    #Make ticks larger
    spectrum.xaxis.major_label_text_font_size = '16pt'
    spectrum.yaxis.major_label_text_font_size = '16pt'

    spectrum.background_fill_color = 'teal'
    spectrum.border_fill_color = 'teal'

    script, div = components(gridplot([plot, radio, optical, spectrum], ncols=2, sizing_mode='stretch_both'))

    kwargs = {'script': script, 'div': div}
    kwargs['title'] = 'bokeh-with-flask'
    return render_template('event.html', event=event, **kwargs)

@app.route('/docs')
def docs():
    return render_template('docs.html')


# @app.route('/contact')
# def contact():
#     return render_template('contacts.html')

# Pass the data to be used by the dropdown menu (decorating)
@app.context_processor
# def get_current_user():
#   return {"grbs": grbs}

def grb_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT(GRB) FROM SQLDataGRBSNe')
    grbs = []
    years = []
    for i in names:
        grbs.append(i[0])
        years.append(str(i[0])[:2])
    length = len(grbs)
    #Get only the unique years
    unique_years = []
    for i in years:
        #There was a problem with NULL SQL values coming in as 'No'
        if i not in unique_years:

            if i=='No':
                continue
            else:
                unique_years.append(i)

    for i in range(len(unique_years)):
        if int(unique_years[i])<30:
            unique_years[i] = ('20'+unique_years[i])
        else:
            unique_years[i] = ('19'+unique_years[i])

    conn.close()
    
    
    return {'grbs': grbs, 'number1':length, 'number2':len(unique_years), 'years':unique_years}


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

# # Table of all the data to be displayed on the webpage
# from flask_table import Table, Col


# # Declare your table
# class GRBTable(Table):
#     name = Col('GRB')
#     description = Col('SN')

# # Or, more likely, load items from your database with something like
# items = ItemModel.query.all()

# # Populate the table
# table = ItemTable(items)

# # Print the html
# print(table.__html__())
# # or just {{ table }} from within a Jinja template 

# Contact form 

from static.emails.forms import ContactForm
from flask import request
import pandas as pd
@app.route('/contact', methods=["GET","POST"])
def get_contact():
    form = ContactForm()
    # here, if the request type is a POST we get the data on contat
    #forms and save them else we return the contact forms html page
    if request.method == 'POST':
        name =  request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        res = pd.DataFrame({'name':name, 'email':email, 'subject':subject ,'message':message}, index=[0])
        res.to_csv('static/emails/emails.csv', mode='a')
        print("The data are saved !")
        return('The data are saved !')
    else:
        return render_template('contacts.html', form=form)

# Run app
if __name__ == "__main__":
    #debug=True lets you do it without rerunning all the time

    app.run(debug = True)