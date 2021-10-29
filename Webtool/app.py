from flask import Flask, render_template, redirect, url_for, flash, send_file, make_response
from werkzeug.exceptions import abort

#Find the txt files with the right names
import glob
import numpy as np
import json

#Pieces for Bokeh
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.layouts import gridplot, Spacer
from bokeh.plotting import figure, output_file, show
from flask import Flask, request, render_template, abort, Response
from bokeh.plotting import figure
from bokeh.embed import components

#Pandas
import pandas as pd

#Things for making updatable plots
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

#Search bar
from wtforms import Form, StringField
class SearchForm(Form):
    object_name = StringField('Search by GRB or SN ID')

#email form
from static.emails.forms import ContactForm

#Graphs with matplotlib
import matplotlib.pyplot as plt

#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect('static/Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(event_id):
    #To determine if we need to search the db by SN or by GRB name
    #Removed the search for '_' since it was always true for some reason. It now works for SN and GRB alone and together.
    if 'GRB' in event_id:
        #GRB202005A_SN2001a -  GRB is 0, 1, 2 so we want from 3 to the end of the split list
        #This solves the GRBs with SNs and without
        grb_name = event_id.split('_')[0][3:]
        conn = get_db_connection()
        event = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE GRB = ? AND PrimarySources!='PRIVATE COM.'", (grb_name,)).fetchall()

        radec = conn.execute('SELECT * FROM RADec WHERE grb_id=?', (grb_name,)).fetchall()
        
        #Round ra and dec to 3dp
        if radec[0]['ra']!=None and radec[0]['dec']!=None:
            ra = round(float(radec[0]['ra']), 3)
            dec = round(float(radec[0]['dec']), 3)
            radec = [ra, dec]

        else:
            ra = 'None'
            dec = 'None'
            radec = [ra, dec]

        #Deals with people entering names that arent in the DB
        if event is None:
            abort(404)
        conn.close()
    

    #This should ideally solve the lone SN cases
    elif 'SN' or 'AT' in event_id:
        sn_name = event_id.split('_')[0][2:]

        #The list was empty because im searching for SN2020oi but the names in the database dont have the SN bit
        conn = get_db_connection()
        event = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE SNe = ? AND PrimarySources!='PRIVATE COM.'", (event_id[2:],)).fetchall()
        
        radec = conn.execute('SELECT * FROM RADec WHERE sn_name=?', (sn_name,)).fetchall()
        
        #Round ra and dec to 3dp
        if radec[0]['ra']!=None and radec[0]['dec']!=None:
            ra = round(float(radec[0]['ra']), 3)
            dec = round(float(radec[0]['dec']), 3)
            radec = [ra, dec]

        else:
            ra = 'None'
            dec = 'None'
            radec = [ra, dec]

        
        if event is None:
            abort(404)
        conn.close()      
    return event, radec

#For the main table
def get_selected_data():
    conn = get_db_connection()
    data = conn.execute('SELECT * FROM SQLDataGRBSNe GROUP BY GRB')
    data2 = []
    for i in data:
        data2.append([i['GRB'], i['SNe'], i['e_iso'], i['T90'], i['z']])
    conn.close()
    return data2
    
def grb_sne_dict():
    conn = get_db_connection()
    data = conn.execute('SELECT GRB, SNe FROM SQLDataGRBSNe GROUP BY GRB')
    grb_sne_dict = {}
    for i in data:
        if i['SNe']!=None:
            grb_sne_dict[i['SNe']] = i['GRB']
    return(grb_sne_dict)

grb_sne = grb_sne_dict()


def grb_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT(GRB) FROM SQLDataGRBSNe WHERE GRB IS NOT NULL')
    grbs = []
    for i in names:
    	grbs.append(i[0])
    conn.close()
    
    return grbs
grbs = grb_names()

#This code goes to the long_grbs folder and gets all the data for the plot
def get_grb_data(event_id):

    #To determine if its an SN only or a GRB only
    if 'GRB' in str(event_id):
        path = './static/long_grbs/'
        files = glob.glob(path+'/*.txt')
        print(files)

        for i in range(len(files)):
            if str(event_id) in str(files[i]):
                k = np.loadtxt(files[i], skiprows=1, unpack=True)
                break
            else:
                k = [[0], [0], [0], [0], [0], [0]]
    else:
        k = [[0], [0], [0], [0], [0], [0]]        
    return(k)

#Extract the SN names from the database
def sne_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT(SNe) FROM SQLDataGRBSNe')
    sne = []
    for i in names:
        
        if i[0] == None:
            continue

        #Theres a piece of scientific notation in one of the columns
        elif 'E' in str(i[0]):
            continue

        #Select only the correct names
        else:
            sne.append(i[0])
    conn.close()
    return sne

app = Flask(__name__)
app.secret_key = 'secretKey'

#The pages we want
#Updatable graphs about the info in the db

    #Z plot
    # print(z)
    # plt.hist(z, bins = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2])
    # plt.xlabel('Redshift')
    # plt.ylabel('Frequency')
    # plt.savefig('static/stats/GRBSNeZ.pdf')

#The homepage and its location
@app.route('/', methods=['POST', 'GET'])
def home():
    #Form
    form = SearchForm(request.form)
    if request.method == 'POST':
        event_id = form.object_name.data

        return redirect(url_for('event', event_id=event_id))
       
    return render_template('home.html', form=form)

@app.route('/plot/e_iso')
def graph_data_grabber():
    conn = get_db_connection()

    #E_iso data, one value per GRB
    data = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE GRB IS NOT NULL AND PrimarySources!='PRIVATE COM.'").fetchall()
    

    #Data for the graphs, remove the duplicates
    e_iso_photometric = []
    e_iso_spectroscopic = []
    grb_name = 'start'

    for i in data:
        if i['e_iso']!=None and '>' not in i['e_iso']:
            if i['GRB']!=grb_name and i['SNe']!=None:
                grb_name = i['GRB']
                e_iso_spectroscopic.append(float(i['e_iso']))


            elif i['GRB']!=grb_name and i['SNe']==None:
                grb_name = i['GRB']
                e_iso_photometric.append(float(i['e_iso'])) 

    e_iso = e_iso_photometric+e_iso_spectroscopic
    

    conn.close()
    #Do graphing
    #E_iso plot

    fig = Figure()
    ax = fig.subplots()
    ax.hist(np.log10(e_iso))
    ax.set_xlabel('E$_{iso}$ (ergs)')
    ax.set_ylabel('Frequency')


    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response


@app.route('/plot/z')
def z_plotter():
    conn = get_db_connection()

    #E_iso data, one value per GRB
    data = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE GRB IS NOT NULL AND PrimarySources!='PRIVATE COM.'").fetchall()
    

    #Data for the graphs, remove the duplicates
    z_photometric  = []
    z_spectroscopic  = []
    grb_name = 'start'
    

    for i in data:
        if i['z']!=None:
            if i['GRB']!=grb_name and i['SNe']!=None:
                grb_name = i['GRB']
                z_spectroscopic.append(float(i['z']))


            elif i['GRB']!=grb_name and i['SNe']==None:
                grb_name = i['GRB']
                z_photometric.append(float(i['z'])) 

    z = z_photometric+z_spectroscopic

    conn.close()
    #Do graphing
    #E_iso plot

    fig = Figure()
    ax = fig.subplots()
    ax.hist(z_photometric, label='Photometric SN', alpha=0.5, edgecolor='black', color='green', bins = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1., 1.1])
    ax.hist(z_spectroscopic, label='Spectroscopic SN', alpha=0.5, edgecolor='black', color='purple', bins = [0., 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1., 1.1])
    ax.legend()
    ax.set_xlabel('Redshift')
    ax.set_ylabel('Frequency')


    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response

    return render_template('home.html', form=form, data=data)

#Be able to select the GRBs by their names and go
#To a specific page, it also plots the XRT data

@app.route('/<event_id>')
def event(event_id):
    source = ColumnDataSource()
    event, radec = get_post(event_id)
    data = get_grb_data(event_id)

    ######################################################################################
    #####X--RAYS##########################################################################
    ######################################################################################
    t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg = data
    # create a new plot with a title and axis labels

    plot = figure(title='X-ray', toolbar_location="right", y_axis_type="log", x_axis_type="log")
    
    # add a line renderer with legend and line thickness
    #plot.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

    #Aesthetics
    plot.title.text_font_size = '20pt'
    plot.title.text_color = 'white'
    plot.title.align = 'center'

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

    ######################################################################################
    #####OPTICAL##########################################################################
    ######################################################################################
    from bokeh.palettes import Category20_20

    optical = figure(title='Optical', toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness

    #Extract and plot the optical photometry data from the photometry file for each SN
    if event[0]['SNe'] != None:

        data = pd.read_csv('./static/SNE-OpenSN-Data/photometry/'+str(event[0]['SNe'])+'.csv')
        if data.empty == True:
            print()
        else:
            bands = set(data['band'])


       
            color = Category20_20.__iter__()
            for j in bands:
                new_df = data.loc[data['band']==j]
                optical.scatter(new_df['time'], new_df['magnitude'], legend_label=str(j), size=10, color=next(color))

        #Aesthetics

        #Title
        optical.title.text_font_size = '20pt'
        optical.title.text_color = 'white'
        optical.title.align = 'center'

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

        optical.background_fill_color = 'white'
        optical.border_fill_color = 'white'


    ######################################################################################
    #####RADIO############################################################################
    ######################################################################################
    radio = figure(title='Radio', toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness
    #radio.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

    #Aesthetics

    #Title
    radio.title.text_font_size = '20pt'
    radio.title.text_color = 'white'
    radio.title.align = 'center'
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

    ######################################################################################
    #####SPECTRA##########################################################################
    ######################################################################################
    spectrum = figure(title='Spectrum', toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness
    #spectrum.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')
        #Aesthetics

    #Title
    spectrum.title.text_font_size = '20pt'
    spectrum.title.text_color = 'white'
    spectrum.title.align = 'center'
    
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


    script, div = components(gridplot([plot, radio, optical, spectrum], ncols=2, merge_tools = False))
    kwargs = {'script': script, 'div': div}
    kwargs['title'] = 'bokeh-with-flask'

    #References
    #Primary
    with open("static/citations.json") as file:
        dict_refs = json.load(file)

    #Secondary
    with open("static/citations2.json") as file2:
        dict_refs2 = json.load(file2)

    #loop through dict refs to get the relevant references
    authors = []
    years = []

    authors2 = []
    years2 = []
    for i in range(len(event)):
        if event[i]['PrimarySources']=='PRIVATE COM.':
            authors.append('Private communication.')
            years.append('')


        elif event[i]['PrimarySources']!=None:

            authors.append(dict_refs[event[i]['PrimarySources']][:-5])
            years.append(dict_refs[event[i]['PrimarySources']][-5:])

        elif event[i]['SecondarySources']!=None:
            authors2.append(dict_refs2[event[i]['SecondarySources']][:-5])
            years2.append(dict_refs2[event[i]['SecondarySources']][-5:])


    #Return everything
    return render_template('event.html', event=event, radec=radec, years=years, authors=authors, years2=years2, authors2=authors2, dict=dict_refs, dict2=dict_refs2, **kwargs)

@app.route('/docs')
def docs():
    return render_template('docs.html')

# Pass the data to be used by the dropdown menu (decorating)
@app.context_processor
# def get_current_user():
#   return {"grbs": grbs}

def grb_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT GRB, SNe FROM SQLDataGRBSNe')
    grbs = []
    years = []
    for i in names:
        if str(i[0])!='None' and str(i[1])!='None':
            if 'AT' in str(i[1]):
                grbs.append('GRB'+str(i[0])+'_'+str(i[1]))
            else:
                grbs.append('GRB'+str(i[0])+'_SN'+str(i[1]))
            
        #years.append(str(i[0])[:2])
        elif str(i[1])=='None':
            grbs.append('GRB'+str(i[0]))

        elif str(i[0])=='None':
            if 'AT' in str(i[1]):
                grbs.append(str(i[1]))
            else:
                grbs.append('SN'+str(i[1]))
    length = len(grbs)

    #Get only the unique years (this is redundant code now because I'm not splitting them by year anymore)
    # unique_years = []
    # for i in years:
    #     #There was a problem with NULL SQL values coming in as 'No'
    #     if i not in unique_years:

    #         if i=='No':
    #             continue
    #         else:
    #             unique_years.append(i)

    # for i in range(len(unique_years)):
    #     if int(unique_years[i])<30:
    #         unique_years[i] = ('20'+unique_years[i])
    #     else:
    #         unique_years[i] = ('19'+unique_years[i])

    conn.close()
    
    
    return {'grbs': grbs, 'number1':length} #, 'number2':len(unique_years), 'years':unique_years}




# Contact form 
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

#Making the search bar run https://flask.palletsprojects.com/en/2.0.x/patterns/wtforms/
# @app.route('/search', methods=['POST', 'GET'])
# def search_bar():
#     form = SearchForm(request.form)
    
#     if request.method == 'POST':
#         #The problem is here somewhere
#         event_id = form.object_name.data
#         #its rediricting to home (url for is / when it should be /form)
#         with app.test_request_context():
#             print('The URL is:', url_for('event', event_id=event_id))
#         #The syntax in this line are definitely correct based on the docs
#         return redirect(url_for('event', event_id=event_id))

    
#     return render_template('form.html', form=form)

# Run app
if __name__ == "__main__":
    #debug=True lets you do it without rerunning all the time

    app.run(debug = True)