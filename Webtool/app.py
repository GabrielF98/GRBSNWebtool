from flask import Flask, current_app, render_template, redirect, url_for, flash, send_file, make_response, Response, request, abort
from werkzeug.exceptions import abort

from flask_bootstrap import Bootstrap

#Find the txt files with the right names
import glob
import numpy as np
import json

#Pieces for Bokeh
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput, HoverTool, Range1d, Label, LabelSet
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from bokeh.layouts import gridplot, Spacer, layout, column, row
from bokeh.plotting import figure, output_file, show
from bokeh.palettes import all_palettes, viridis

#Pandas
import pandas as pd

#Import os
import os

#File processing
import zipfile
import shutil

#Astropy
from astropy.time import Time

#Things for making updatable plots
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

#Search bar
from wtforms import Form, StringField, SubmitField

class SearchForm(Form):
    object_name = StringField('Search by GRB or SN ID')
    submit1 = SubmitField('Submit')

#Pulling the data you want to the table on the homepage #Currently this isnt being used on master
class TableForm(Form):
    max_z = StringField('Min. Z')
    min_z = StringField('Max. Z')
    max_eiso = StringField('Max. E$_{iso}$')
    min_eiso = StringField('Min. E$_{iso}$')
    submit2 = SubmitField('Submit')

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
    conn = get_db_connection()
    if 'GRB' in event_id:
        #GRB202005A_SN2001a -  GRB is 0, 1, 2 so we want from 3 to the end of the split list
        #This solves the GRBs with SNs and without
        grb_name = event_id.split('_')[0][3:]
        event = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE GRB = ?", (grb_name,)).fetchall()

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
    

    #This should ideally solve the lone SN cases
    elif 'SN' or 'AT' in event_id:
        sn_name = event_id[2:]

        #The list was empty because im searching for SN2020oi but the names in the database dont have the SN bit
        
        event = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE SNe = ?", (sn_name,)).fetchall()
        
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

#For the main table on the homepage
def table_query(max_z, min_z, max_eiso, min_eiso):
    conn = get_db_connection()
    data = conn.execute('SELECT GRB, SNe, AVG(e_iso), AVG(T90), AVG(z) FROM SQLDataGRBSNe WHERE CAST(e_iso as FLOAT)>? AND CAST(e_iso as FLOAT)<? AND CAST(z as FLOAT)>? AND CAST(z as FLOAT)<? GROUP BY GRB', (min_eiso, max_eiso, min_z, max_z))
    #data = conn.execute('SELECT * FROM [Display Table] WHERE z<0.1;')
    data2 = []
    for i in data:
        data2.append([i['GRB'], i['SNe'], i['AVG(e_iso)'], i['AVG(T90)'], i['AVG(z)']])
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

def grb_sne_dict():
    conn = get_db_connection()
    data = conn.execute('SELECT GRB, SNe FROM SQLDataGRBSNe GROUP BY GRB')
    grb_sne_dict = {}
    for i in data:
        if i['SNe']!=None:
            grb_sne_dict[i['SNe']] = i['GRB']
    return(grb_sne_dict)

grb_sne = grb_sne_dict()

#This code goes to the long_grbs folder and gets all the data for the plot
def get_grb_data(event_id):

    #To determine if its an SN only or a GRB only
    if 'GRB' in str(event_id):
        event_id = event_id.split('_')[0][3:]
        path = './static/long_grbs/'
        files = glob.glob(path+'/*.txt')
        #print(files)

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

sne = sne_names()

app = Flask(__name__)
app.secret_key = 'secretKey'

#The homepage and its location
@app.route('/', methods=['POST', 'GET'])
def home():
    #Connect to db
    conn = get_db_connection()

    #Ok new plan
    #Going to give it a go with the UNION and INTERSECT commands
    initial_query = (f"SELECT GRB, SNe, GROUP_CONCAT(e_iso), GROUP_CONCAT(z), GROUP_CONCAT(T90) FROM SQLDataGRBSNe GROUP BY GRB, SNe ORDER BY GRB, SNe;")
    data = conn.execute(initial_query).fetchall()

    form = SearchForm(request.form)
    
    if request.method == 'POST':
        event_id = form.object_name.data
        print(event_id)
        if str(event_id)[2:] in sne: #if they search an SN
            return redirect(url_for('event', event_id=event_id))
        elif str(event_id)[3:] in grbs: #if they search an GRB
            return redirect(url_for('event', event_id=event_id))
        else:
            flash('This object is not in our database.')
            return render_template('home.html', form=form, data=data)
    return render_template('home.html', form=form, data=data)

@app.route('/plot/e_iso')
def graph_data_grabber():
    conn = get_db_connection()

    #E_iso data, one value per GRB
    data = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE GRB IS NOT NULL").fetchall()
    

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
    ax.hist(np.log10(e_iso), color='green', alpha=0.5)
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
    event, radec = get_post(event_id)
    data = get_grb_data(event_id)

    #References
    #Primary
    with open("static/citations.json") as file:
        dict_refs = json.load(file)

    #Secondary
    with open("static/citations2.json") as file2:
        dict_refs2 = json.load(file2)

    #Find out how many of these references are needed
    needed_dict = {} 
    for i in range(len(event)):
        if event[i]['PrimarySources']!=None:
            needed_dict[event[i]['PrimarySources']] = dict_refs[event[i]['PrimarySources']]
        elif event[i]['SecondarySources']!=None:
            needed_dict[event[i]['SecondarySources']] = dict_refs[event[i]['SecondarySources']]

    ######################################################################################
    #############DATA FOR THE PLOTS#######################################################
    ######################################################################################

    ######################################################################################
    #####X--RAYS##########################################################################
    ######################################################################################
    t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg = data
    # create a new plot with a title and axis labels

    xray = figure(title='X-ray', toolbar_location="right", y_axis_type="log", x_axis_type="log")
    
    # add a line renderer with legend and line thickness
    xray.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

    #Aesthetics
    xray.title.text_font_size = '20pt'
    xray.title.text_color = 'black'
    xray.title.align = 'center'

    #Axis font size
    xray.yaxis.axis_label_text_font_size = '16pt'
    xray.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    xray.xaxis.axis_label_text_color = 'black'
    xray.xaxis.major_label_text_color = 'black'

    xray.yaxis.axis_label_text_color = 'black'
    xray.yaxis.major_label_text_color = 'black'

    #Tick colors 
    xray.xaxis.major_tick_line_color = 'black'
    xray.yaxis.major_tick_line_color = 'black'

    xray.xaxis.minor_tick_line_color = 'black'
    xray.yaxis.minor_tick_line_color = 'black'

    #Axis labels
    xray.xaxis.axis_label = 'Time [sec]'
    xray.yaxis.axis_label = 'Flux (0.3-10keV) [erg/cm^2/sec]'

    #Axis Colors
    xray.xaxis.axis_line_color = 'black'
    xray.yaxis.axis_line_color = 'black'

    #Make ticks larger
    xray.xaxis.major_label_text_font_size = '16pt'
    xray.yaxis.major_label_text_font_size = '16pt'

    xray.background_fill_color = 'white'
    xray.border_fill_color = 'white'



    #script, div = components(plot)

    ######################################################################################
    #####OPTICAL##########################################################################
    ######################################################################################
    from bokeh.palettes import Category20_20

    optical = figure(title='Optical (GRB+SN)', toolbar_location="right", y_axis_type="log", x_axis_type="log")
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
            optical.y_range.flipped = True

    #Aesthetics

    #Title
    optical.title.text_font_size = '20pt'
    optical.title.text_color = 'black'
    optical.title.align = 'center'

    #Axis font size
    optical.yaxis.axis_label_text_font_size = '16pt'
    optical.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    optical.xaxis.axis_label_text_color = 'black'
    optical.xaxis.major_label_text_color = 'black'

    optical.yaxis.axis_label_text_color = 'black'
    optical.yaxis.major_label_text_color = 'black'

    #Tick colors 
    optical.xaxis.major_tick_line_color = 'black'
    optical.yaxis.major_tick_line_color = 'black'

    optical.xaxis.minor_tick_line_color = 'black'
    optical.yaxis.minor_tick_line_color = 'black'

    #Axis labels
    optical.xaxis.axis_label = 'Time [MJD]'
    optical.yaxis.axis_label = 'Apparent Magnitude'

    #Axis Colors
    optical.xaxis.axis_line_color = 'black'
    optical.yaxis.axis_line_color = 'black'

    #Make ticks larger
    optical.xaxis.major_label_text_font_size = '16pt'
    optical.yaxis.major_label_text_font_size = '16pt'

    optical.background_fill_color = 'white'
    optical.border_fill_color = 'white'


    ######################################################################################
    #####RADIO############################################################################
    ######################################################################################
    radio = figure(title='Radio (GRB)', toolbar_location="right", y_axis_type="log", x_axis_type="log")
    # add a line renderer with legend and line thickness
    #radio.scatter(t, flux, legend_label="Swift/XRT", size=10, fill_color='orange')

    #Aesthetics

    #Title
    radio.title.text_font_size = '20pt'
    radio.title.text_color = 'black'
    radio.title.align = 'center'
    #Axis font size
    radio.yaxis.axis_label_text_font_size = '16pt'
    radio.xaxis.axis_label_text_font_size = '16pt'

    #Font Color 
    radio.xaxis.axis_label_text_color = 'black'
    radio.xaxis.major_label_text_color = 'black'

    radio.yaxis.axis_label_text_color = 'black'
    radio.yaxis.major_label_text_color = 'black'

    #Tick colors 
    radio.xaxis.major_tick_line_color = 'black'
    radio.yaxis.major_tick_line_color = 'black'

    radio.xaxis.minor_tick_line_color = 'black'
    radio.yaxis.minor_tick_line_color = 'black'

    #Axis labels
    radio.xaxis.axis_label = 'Time [sec]'
    radio.yaxis.axis_label = 'Flux Density [mJy]'

    #Axis Colors
    radio.xaxis.axis_line_color = 'black'
    radio.yaxis.axis_line_color = 'black'

    #Make ticks larger
    radio.xaxis.major_label_text_font_size = '16pt'
    radio.yaxis.major_label_text_font_size = '16pt'

    radio.background_fill_color = 'white'
    radio.border_fill_color = 'white'

    ######################################################################################
    #####SNe SPECTRA######################################################################
    ######################################################################################
    #Selection tools we want to display
    select_tools = ['box_zoom', 'pan', 'wheel_zoom', 'save', 'reset'] 

    #Figure
    spectrum = figure(title='Spectrum (SN)', toolbar_location="right", tools=select_tools)
    
    #Blank tooltips
    tooltips = []

    #Spectra sources
    spec_refs = []
    spec_cites = []

    if event[0]['SNe'] != None:

        #Access the data in the files for the SNe Spectra
        path = './static/SNE-OpenSN-Data/spectraJSON/'+str(event[0]['SNe'])+'/'
        files = glob.glob(path+'/*.json')

        color = viridis(len(files)) #Colormap to be used - 45 is the max number of spectra im expecting for a single event 

         
        max_spec = np.zeros(len(files))
        min_spec = np.zeros(len(files))
        for i in range(len(files)):
            with open(files[i]) as json_file:
                data_i = json.load(json_file)

                #Split the data into two lists, one wavelengths and one flux
                wavelength, flux = zip(*data_i['SN'+str(event[0]['SNe'])]['spectra']['data'])
                
                wavelength, flux = list(wavelength), list(flux)

                #Calculating the extent of the limits on the plots
                float_flux = []
                for j in flux:
                    float_flux.append(float(j))

                max_spec[i] = max(float_flux)
                min_spec[i] = min(float_flux)

                #Create a dictionary of the necessary info
                data_dict = {'wavelength': wavelength, 'flux': float_flux,
                            'time': [data_i['SN'+str(event[0]['SNe'])]['spectra']['time']]*len(wavelength)}

                # spectra_time = Time(data_i['SN'+str(event[0]['SNe'])]['spectra']['time'], format='mjd')
                # data_dict['time'] = [spectra_time]*len(wavelength)
                #SOURCES
                sources = data_i['SN'+str(event[0]['SNe'])]['spectra']['source']
                source_indices = [] #This is supposed to show the number to be assigned to a particular source. 

                for k in range(len(sources)):
                    #Check if we are already using this reference for some of the data in the tables or for another spectrum
                    if sources[k]['url'] in needed_dict.keys():
                        source_indices.append(list(needed_dict.keys()).index(sources[k]['url'])+1)

                    elif sources[k]['url'] in spec_refs:
                        source_indices.append(spec_refs.index(sources[k]['url'])+3)

                    else:
                        spec_refs.append(sources[k]['url'])
                        spec_cites.append(sources[k]['name'])
                        source_indices.append(spec_refs.index(sources[k]['url'])+3)

                data_dict['sources'] = [source_indices]*len(wavelength)
                data_dict['wave_unit'] = [data_i['SN'+str(event[0]['SNe'])]['spectra']['u_wavelengths']]*len(wavelength)
                data_dict['flux_unit'] = [data_i['SN'+str(event[0]['SNe'])]['spectra']['u_fluxes']]*len(wavelength)

                #Convert the dict to a column data object
                data_source = ColumnDataSource(data_dict)

                #Tooltips of what will display in the hover mode
                # Format the tooltip
                tooltips = [
                            ('Wavelength [Å]', '@wavelength{0}'),
                            ('Wavelength unit', '@wave_unit'),
                            ('Flux', '@flux'),
                            ('Flux unit', '@flux_unit'),
                            ('Date [MJD]', '@time'),
                            ('Source', '@sources') 
                           ]


                spectrum.line('wavelength', 'flux', source=data_source, color=color[i])
                
        # Add the HoverTool to the figure
        spectrum.add_tools(HoverTool(tooltips=tooltips))

        
        #Aesthetics    
        #Title
        spectrum.title.text_font_size = '20pt'
        spectrum.title.text_color = 'black'
        spectrum.title.align = 'center'

        #Axis font size
        spectrum.yaxis.axis_label_text_font_size = '16pt'
        spectrum.xaxis.axis_label_text_font_size = '16pt'

        #Font Color 
        spectrum.xaxis.axis_label_text_color = 'black'
        spectrum.xaxis.major_label_text_color = 'black'

        spectrum.yaxis.axis_label_text_color = 'black'
        spectrum.yaxis.major_label_text_color = 'black'

        #Tick colors 
        spectrum.xaxis.major_tick_line_color = 'black'
        spectrum.yaxis.major_tick_line_color = 'black'

        spectrum.xaxis.minor_tick_line_color = 'black'
        spectrum.yaxis.minor_tick_line_color = 'black'

        #Axis labels
        spectrum.xaxis.axis_label = 'Wavelength [Å]'
        spectrum.yaxis.axis_label = 'Flux'

        #Axis Colors
        spectrum.xaxis.axis_line_color = 'black'
        spectrum.yaxis.axis_line_color = 'black'

        #Make ticks larger
        spectrum.xaxis.major_label_text_font_size = '16pt'
        spectrum.yaxis.major_label_text_font_size = '16pt'

        spectrum.background_fill_color = 'white'
        spectrum.border_fill_color = 'white'
        
        #Range
        print('The min and max are', min_spec, max_spec)
        spectrum.y_range=Range1d(min(min_spec)-0.1*min(min_spec), 0.1*max(max_spec)+max(max_spec))

    else:
        # Add the HoverTool to the figure
        spectrum.add_tools(HoverTool(tooltips=tooltips))

        
        #Aesthetics    
        #Title
        spectrum.title.text_font_size = '20pt'
        spectrum.title.text_color = 'red'
        spectrum.title.align = 'center'

        #Axis font size
        spectrum.yaxis.axis_label_text_font_size = '16pt'
        spectrum.xaxis.axis_label_text_font_size = '16pt'

        #Font Color 
        spectrum.xaxis.axis_label_text_color = 'black'
        spectrum.xaxis.major_label_text_color = 'black'

        spectrum.yaxis.axis_label_text_color = 'black'
        spectrum.yaxis.major_label_text_color = 'black'

        #Tick colors 
        spectrum.xaxis.major_tick_line_color = 'black'
        spectrum.yaxis.major_tick_line_color = 'black'

        spectrum.xaxis.minor_tick_line_color = 'black'
        spectrum.yaxis.minor_tick_line_color = 'black'

        #Axis labels
        spectrum.xaxis.axis_label = 'Wavelength'
        spectrum.yaxis.axis_label = 'Flux'

        #Axis Colors
        spectrum.xaxis.axis_line_color = 'black'
        spectrum.yaxis.axis_line_color = 'black'

        #Make ticks larger
        spectrum.xaxis.major_label_text_font_size = '16pt'
        spectrum.yaxis.major_label_text_font_size = '16pt'

        spectrum.background_fill_color = 'white'
        spectrum.border_fill_color = 'white'

        citation = Label(x=70, y=70, x_units='screen', y_units='screen',
                 text='NO DATA', render_mode='css',
                 border_line_color='black', border_line_alpha=1.0,
                 background_fill_color='white', background_fill_alpha=1.0)
        spectrum.add_layout(citation)

    script, div = components(gridplot([xray, radio, optical, spectrum], ncols=2, merge_tools = False))
    kwargs = {'script': script, 'div': div}
    kwargs['title'] = 'bokeh-with-flask'

    #Return everything
    return render_template('event.html', event=event, radec=radec, dict=dict_refs, dict2=dict_refs2, spec_refs=spec_refs, spec_cites=spec_cites, **kwargs)


import shutil
# @app.route('/downloads/<directory>', methods=['GET', 'POST'])
# def get_files(directory):
#     #Creat the output name for the zipped directory
#     output_filename = str(directory)

#     #
#     k = shutil.make_archive(output_filename, 'zip', current_app.root_path+'/static/SourceData/'+directory)
    
#     #Zip the folder
#     return send_file(k, as_attachment=True)

@app.route('/downloads/<directory>', methods=['GET', 'POST'])
def get_files2(directory):
    filestream=io.BytesIO()
    with zipfile.ZipFile(filestream, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
        for file in os.walk('/static/SourceData/'+directory):
            zipf.write(file, filestream)
    filestream.seek(0)
    return send_file(filestream, attachment_filename=directory+'.zip', 
                      as_attachment=True, mimetype='application/zip')


@app.route('/docs')
def docs():
    return render_template('docs.html')



@app.route('/graphing', methods=['GET', 'POST']) #Graphing tool
def graphs():
    category_dict = {'all':'all events', 'orphan':'Orphan GRB Afterglows', 'spec':'Spectroscopic SNe Only', 'phot':'Photometric SNe Only'}
    name_dict = {'e_iso':'Eiso [erg]', 'z':'Redshift', 
    'ni_m':u'SN Nickel Mass [M\u2609]', 'ej_m':u'SN Ejecta Mass [M\u2609]',
     'E_p':"GRB Peak Energy [erg]", 'e_k':'GRB Kinetic Energy [erg]',
      'T90':"T90 [sec]"}

    axis = {'e_iso':'log', 'z':'linear', 'ni_m':'linear', 'ej_m':'linear',
     'E_p':"linear", 'e_k':'log', 'T90':"log"}
    if request.method=='POST':
        category = request.form.getlist('selectors1')

        x = request.form.getlist('selectors2')
        y = request.form.getlist('selectors3')

        conn = get_db_connection() #Connect to DB

        if category[0]=='all':
            #Get the data for the plots
            data = conn.execute("SELECT DISTINCT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY GRB, SNe".format(a=x[0], b=y[0])).fetchall()
        
        elif category[0]=='orphan':
            #Get the data for the plots
            data = conn.execute("SELECT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE GRB IS NULL AND {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY SNe".format(a=x[0], b=y[0])).fetchall()
        
        elif category[0]=='spec':
            #Get the data for the plots
            data = conn.execute("SELECT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE SNe IS NOT NULL AND {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY SNe".format(a=x[0], b=y[0])).fetchall()

        elif category[0]=='phot':
        #Get the data for the plots
            data = conn.execute("SELECT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE SNe IS NULL  AND {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY GRB".format(a=x[0], b=y[0])).fetchall()
    


        #Data for the graphs, remove the duplicates
        x_data = []
        y_data = []
        x_data_upperx = []
        x_data_uppery = []
        x_data_lowerx = []
        x_data_lowery = []

        
        y_data_upperx = []
        y_data_uppery = []
        y_data_lowerx = []
        y_data_lowery = []

        grb_name = []
        sne_name = []
        raw_x = []
        raw_y = []

        #Loop rows returned from SQL
        for row in data:
            grb_name.append(row[0])
            sne_name.append(row[1])
            #
            raw_x.append(str(row[2]).split(',')[0])
            raw_y.append(str(row[3]).split(',')[0])
            #Remove the first item from the returned list for plotting
            if str(row[2]).split(',')[0]!='None' and str(row[3]).split(',')[0]!='None':
                
                

                if '<' in str(row[2]).split(',')[0]:
                    print('case1'+str(row[2]).split(',')[0])
                    x_data_upperx.append(float(str(row[2]).split(',')[0][1:]))
                    y_data_upperx.append(float(str(row[3]).split(',')[0][1:]))
                elif '>' in str(row[2]).split(',')[0]:
                    print('case2'+row[2].split(',')[0])
                    x_data_lowerx.append(float(str(row[2]).split(',')[0][1:]))
                    y_data_lowerx.append(float(str(row[3]).split(',')[0][1:]))
                elif '<' in str(row[3]).split(',')[0]:
                    print('case3'+row[3].split(',')[0])
                    x_data_upperx.append(float(str(row[2]).split(',')[0][1:]))
                    y_data_upperx.append(float(str(row[3]).split(',')[0][1:]))
                elif '>' in str(row[3]).split(',')[0]:
                    print('case4'+row[3].split(',')[0])
                    x_data_lowerx.append(float(str(row[2]).split(',')[0][1:]))
                    y_data_lowerx.append(float(str(row[3]).split(',')[0][1:]))
                else:
                    x_data.append(float(str(row[2]).split(',')[0]))
                    y_data.append(float(str(row[3]).split(',')[0]))



        #Zip the data for the downloadable files
        if request.form.get('download'):
            download = np.column_stack((grb_name, sne_name, raw_x, raw_y))
            s = io.StringIO()
            dwnld = np.savetxt(s, download, delimiter=' ', fmt='%s')
            s.seek(0)
            #Make the response
            resp = Response(s, mimetype='text/csv')

            resp.headers.set("Content-Disposition", "attachment", filename="grbsntool.txt")
            return resp
            

        #Place the plotting data in a dict (the ones that arent uppper/lower limits)
        data_dict = {x[0]:x_data, y[0]:y_data}

        #Convert the dict to a column data object
        data_source = ColumnDataSource(data_dict)
        
        #Plot the data
        #graph = figure(title=str(name_dict[x[0]])+' vs. '+str(name_dict[y[0]])+'\n for '+str(category_dict[category[0]]), x_axis_type=str(axis[x[0]]), y_axis_type=str(axis[y[0]]), toolbar_location="right")
        graph = figure(x_axis_type=str(axis[x[0]]), y_axis_type=str(axis[y[0]]), toolbar_location="right")
        
        graph.circle(x[0], y[0], source=data_source, size=10, fill_color='orange')
        graph.inverted_triangle(x_data_upperx, x_data_uppery, size=10, fill_color='blue')
        graph.triangle(x_data_lowerx, x_data_lowery, size=10, fill_color='red')

        graph.inverted_triangle(y_data_upperx, y_data_uppery, size=10, fill_color='red')
        graph.triangle(y_data_lowerx, y_data_lowery, size=10, fill_color='red')
        
        #Aesthetics
        #Title
        graph.title.text_font_size = '13pt'
        graph.title.text_color = 'black'
        graph.title.align = 'center'
    
        #Axis labels
        graph.xaxis.axis_label = name_dict[x[0]]
        graph.yaxis.axis_label = name_dict[y[0]]

        graph.xaxis.axis_label_text_font_size = '13pt'
        graph.yaxis.axis_label_text_font_size = '13pt'

        #Axis Colors
        graph.xaxis.axis_line_color = 'black'
        graph.yaxis.axis_line_color = 'black'

        #Make ticks larger
        graph.xaxis.major_label_text_font_size = '13pt'
        graph.yaxis.major_label_text_font_size = '13pt'

        script, div = components(graph)
        kwargs = {'script': script, 'div': div}
        kwargs['title'] = 'bokeh-with-flask'

        return render_template('graphs.html', **kwargs)

    else:
        graph = figure(plot_width=400, plot_height=400,title=None, toolbar_location="below")
        
        script, div = components(graph)
        kwargs = {'script': script, 'div': div}
        kwargs['title'] = 'bokeh-with-flask'    
        return render_template('graphs.html', **kwargs)
    
# Likely not needed anymore
# #Dowload the txt generated whilst generating the plot on the graphs page
# @app.route('/download')
# def downloader():
#     print('banana2')
#     s = io.StringIO()
#     dwnld = np.savetxt(s, request.args.get('datalist'))
#     s.seek(0)
#     #Make the response
#     resp = make_response(s, mimetype='text')

#     resp.headers.set("Content-Disposition", "attachment", filename="grbsntool.txt")
#     return resp

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

# Run app
if __name__ == "__main__":
    #debug=True lets you do it without rerunning all the time

    app.run(debug = True)