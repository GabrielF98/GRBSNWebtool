# Imports
import ast  # Convert strings to lists
import glob  # Find the txt files with the right names
import io  # Downloadable zipfiles and for updateable plots
import json  # Reading in data
import math
import os  # Import os to find files in the event folders
import sqlite3  # Database access
import zipfile  # Creating zipfiles for download
from os.path import exists  # Check if a file exists

import numpy as np
import pandas as pd  # Pandas
from astropy.time import Time  # Converting MJD to UTC
from bokeh.embed import components
from bokeh.layouts import layout

# Pieces for Bokeh
from bokeh.models import ColumnDataSource, HoverTool, Label, Legend, Range1d
from bokeh.palettes import Category20_20, d3, viridis
from bokeh.plotting import figure
from bokeh.transform import factor_cmap, factor_mark

# Basic flask stuff
from flask import (
    Blueprint,
    Flask,
    Response,
    abort,
    current_app,
    flash,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

# API
from flask_restx import Api, Resource, reqparse

# Search bars
from flask_wtf import FlaskForm

# Matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.interpolate import interp1d

# Errors for pages that dont exist
from werkzeug.exceptions import abort

# Forms
from wtforms import StringField, SubmitField
from wtforms.validators import Optional

#################################
#################################
# Flask app stuff ###############
#################################
#################################


#################################
#################################
# Bokeh stuff ###################
#################################
#################################


# Create config.py file
with open("instance/config.py", "w") as f:
    code = str(os.urandom(32).hex())
    f.write(("SECRET_KEY = '" + code + "'"))

# Search on the homepage


class SearchForm(FlaskForm):
    object_name = StringField("Search by GRB or SN ID")
    submit1 = SubmitField("Submit")


# Advanced Search


class TableForm(FlaskForm):
    object_name = StringField("", validators=[Optional()])
    min_z = StringField("Min. Z", validators=[Optional()])
    max_z = StringField("Max. Z", validators=[Optional()])
    min_t90 = StringField("Min. T$_{90}$ [sec]", validators=[Optional()])
    max_t90 = StringField("Max. T$_{90}$ [sec]", validators=[Optional()])
    max_eiso = StringField("Max. E$_{iso}$ [ergs]", validators=[Optional()])
    min_eiso = StringField("Min. E$_{iso}$ [ergs]", validators=[Optional()])
    min_nim = StringField("Max. M$_{ni}$ [M$_{\odot}$]", validators=[Optional()])
    max_nim = StringField("Min. M$_{ni}$ [M$_{\odot}$]", validators=[Optional()])
    max_ejm = StringField("Max. M$_{ej}$ [M$_{\odot}$]", validators=[Optional()])
    min_ejm = StringField("Min. M$_{ej}$ [M$_{\odot}$]", validators=[Optional()])
    max_epeak = StringField("Max. E$_{p}$ [keV]", validators=[Optional()])
    min_epeak = StringField("Min. E$_{p}$ [keV]", validators=[Optional()])
    max_ek = StringField("Max. E$_{k}$ [erg]", validators=[Optional()])
    min_ek = StringField("Min. E$_{k}$ [erg]", validators=[Optional()])
    submit2 = SubmitField("Search")


# Add the bit for the database access:


def get_db_connection():
    conn = sqlite3.connect("static/Masterbase.db")
    conn.row_factory = sqlite3.Row
    return conn


# Return the database data based on the name of the event


def get_post(event_id):
    # To determine if we need to search the db by SN or by GRB name
    # Removed the search for '_' since it was always true for some reason. It now works for SN and GRB alone and together.
    conn = get_db_connection()
    if "GRB" in event_id:
        # GRB202005A-SN2001a -  GRB is 0, 1, 2 so we want from 3 to the end of the split list
        # This solves the GRBs with SNs and without
        grb_name = event_id.split("-")[0][3:]

        # The main db table with most of the info
        event = conn.execute(
            "SELECT * FROM SQLDataGRBSNe WHERE GRB = ?", (grb_name,)
        ).fetchall()
        # Table with triggertimes
        radec = conn.execute(
            "SELECT * FROM TrigCoords WHERE grb_id=?", (grb_name,)
        ).fetchall()
        # Table with the peak times and mags in each bang
        peakmags = conn.execute(
            "SELECT * FROM PeakTimesMags WHERE grb_id=?", (grb_name,)
        ).fetchall()

        # Deals with people entering names that arent in the DB
        if event is None:
            abort(404)

    # This should ideally solve the lone SN cases
    else:
        sn_name = event_id[2:]

        # The main db table with most of the info
        event = conn.execute(
            "SELECT * FROM SQLDataGRBSNe WHERE SNe = ?", (sn_name,)
        ).fetchall()
        # Table with triggertimes
        radec = conn.execute(
            "SELECT * FROM TrigCoords WHERE sn_name=?", (sn_name,)
        ).fetchall()
        # Table with the peak times and mags in each bang
        peakmags = conn.execute(
            "SELECT * FROM PeakTimesMags WHERE sn_name=?", (sn_name,)
        ).fetchall()

        if event is None:
            abort(404)
    conn.close()
    return event, radec, peakmags


# Query the main table on the homepage


def table_query(max_z, min_z, max_eiso, min_eiso):
    conn = get_db_connection()
    data = conn.execute(
        "SELECT GRB, SNe, AVG(e_iso), AVG(T90), AVG(z) FROM SQLDataGRBSNe WHERE CAST(e_iso as FLOAT)>? AND CAST(e_iso as FLOAT)<? AND CAST(z as FLOAT)>? AND CAST(z as FLOAT)<? GROUP BY GRB",
        (min_eiso, max_eiso, min_z, max_z),
    )
    # data = conn.execute('SELECT * FROM [Display Table] WHERE z<0.1;')
    data2 = []
    for i in data:
        data2.append([i["GRB"], i["SNe"], i["AVG(e_iso)"], i["AVG(T90)"], i["AVG(z)"]])
    conn.close()

    return data2


# Get a dictionary of grb-sn pairs for ease of use in some functions later


def sne_grb_dict():
    conn = get_db_connection()
    data = conn.execute("SELECT GRB, SNe FROM SQLDataGRBSNe GROUP BY GRB")
    sne_grb_dict = {}
    for i in data:
        if i["SNe"] != None:
            sne_grb_dict[i["SNe"]] = i["GRB"]
    return sne_grb_dict


def grb_sne_dict():
    conn = get_db_connection()
    data = conn.execute("SELECT GRB, SNe FROM SQLDataGRBSNe GROUP BY SNe")
    grb_sne_dict = {}
    for i in data:
        if i["GRB"] != None:
            grb_sne_dict[i["GRB"]] = i["SNe"]
    return grb_sne_dict


grb_sne = grb_sne_dict()
sne_grb = sne_grb_dict()


def event_id_maker(partial_event, grb_sne=grb_sne, sne_grb=sne_grb):
    if "GRB" in partial_event:
        if grb_sne[partial_event[3:]] is not None:
            event_id = partial_event + "-SN" + grb_sne[partial_event[3:]]
        else:
            event_id = partial_event
    else:
        if partial_event[:2] == "SN":
            if sne_grb[partial_event[2:]] is not None:
                event_id = "GRB" + sne_grb[partial_event[2:]] + "-" + partial_event
            else:
                event_id = partial_event
        else:
            if sne_grb[partial_event] is not None:
                event_id = "GRB" + sne_grb[partial_event] + "-" + partial_event
            else:
                event_id = partial_event

    return event_id


# Get all the GRB names


def grb_names():
    conn = get_db_connection()
    names = conn.execute(
        "SELECT DISTINCT(GRB) FROM SQLDataGRBSNe WHERE GRB IS NOT NULL"
    )
    grbs = []
    for i in names:
        grbs.append(i[0])
    conn.close()

    return grbs


grbs = grb_names()

# Extract the SN names from the database


def sne_names():
    conn = get_db_connection()
    names = conn.execute("SELECT DISTINCT(SNe) FROM SQLDataGRBSNe")
    sne = []
    for i in names:

        if i[0] == None:
            continue

        # Theres a piece of scientific notation in one of the columns
        elif "E" in str(i[0]):
            continue

        # Select only the correct names
        else:
            sne.append(i[0])
    conn.close()
    return sne


sne = sne_names()


def processing_tag(event_id, band):
    df = pd.read_csv("static/SourceData/tags.csv")
    df2 = df[df["Name"] == event_id]
    tag = str(df2.iloc[0][band])
    if tag == "Yes":
        tag = "Pending"

    else:
        tag = "No Data"

    return tag


# Creating the instance of the app
app = Flask(__name__, instance_relative_config=True)
blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(blueprint)
app.register_blueprint(blueprint)
app.config.from_pyfile("config.py")


@app.context_processor
def grb_names():
    conn = get_db_connection()
    names = conn.execute("SELECT DISTINCT GRB, SNe FROM SQLDataGRBSNe")
    grbs = []
    for i in names:
        if str(i[0]) != "None" and str(i[1]) != "None":
            if str(i[1][:4]).isnumeric():
                grbs.append("GRB" + str(i[0]) + "-SN" + str(i[1]))
            else:
                grbs.append("GRB" + str(i[0]) + "-" + str(i[1]))

        elif str(i[1]) == "None":
            grbs.append("GRB" + str(i[0]))

        elif str(i[0]) == "None":
            if str(i[1][:4]).isnumeric():
                grbs.append("SN" + str(i[1]))
            else:
                grbs.append(str(i[1]))

    length = len(grbs)
    conn.close()

    return {"grbs": grbs[::-1], "number1": length}


@app.errorhandler(404)
def page_not_found():
    return render_template("404.html", title="404"), 404


# API page
parser = reqparse.RequestParser()
parser.add_argument(
    "event", type=str, help="You need to provide the name of a GRB-SN.", location="args"
)


@api.route("/get-event")
class Downloads(Resource):
    api.doc(parser=parser)

    # @api.representation('application/octet-stream')
    def get(self):
        args = parser.parse_args()
        folder = args["event"]
        print(folder)
        filestream = io.BytesIO()
        with zipfile.ZipFile(
            filestream, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zipf:
            for file in os.listdir(
                current_app.root_path + "/static/SourceData/" + folder + "/"
            ):
                zipf.write(
                    current_app.root_path + "/static/SourceData/" + folder + "/" + file,
                    folder + "/" + file,
                )
        filestream.seek(0)
        return send_file(
            filestream, download_name="Observations.zip", as_attachment=True
        )


@api.route(
    "/filteredbyredshift/max_redshift_<max_redshift>+min_redshift_<min_redshift>"
)
class Downloads2(Resource):
    def get(self, max_redshift, min_redshift):

        conn = get_db_connection()

        names = conn.execute(
            "SELECT DISTINCT GRB, SNe from SQLDataGRBSNe WHERE z>? AND z<?",
            (
                min_redshift,
                max_redshift,
            ),
        ).fetchall()

        directory_list = []
        for name in names:
            print(name[0])
            if name["GRB"] == None:
                directory_list.append("SN" + name["SNe"])

            elif name["SNe"] == None:
                directory_list.append("GRB" + name["GRB"])

            else:
                if "AT" in name["SNe"]:
                    directory_list.append("GRB" + name["GRB"] + "-" + name["SNe"])
                else:
                    directory_list.append(
                        "GRB" + name["GRB"] + "-" + "SN" + name["SNe"]
                    )

        filestream = io.BytesIO()
        with zipfile.ZipFile(
            filestream, mode="w", compression=zipfile.ZIP_DEFLATED
        ) as zipf:
            for folder in directory_list:
                for file in os.listdir(
                    current_app.root_path + "/static/SourceData/" + folder + "/"
                ):
                    zipf.write(
                        current_app.root_path
                        + "/static/SourceData/"
                        + folder
                        + "/"
                        + file,
                        folder + "/" + file,
                    )
        filestream.seek(0)
        return send_file(
            filestream, download_name="Observations.zip", as_attachment=True
        )


def plot_optical(event):
    # Select the optical master file and import it
    optical = pd.read_csv(
        os.path.join(
            app.root_path, "static/SourceData/", event, event + "_Optical_Master.txt"
        ),
        sep="\t",
    )

    # Extract info about the filters in the data
    bands = list(set(list(optical["band"])))

    # Choose colours/fillstyles for the plots
    colours = [
        "#D81B60",
        "#1E88E5",
        "#FFC107",
        "#004D40",
        "#6661B9",
        "#9F48E1",
        "#444297",
    ]
    fills = ["none", "full"]

    # Choose an offset for the data in the plot
    offset = 1

    # Get the limits for the plots
    max_time = np.max(optical["time"])
    min_time = np.min(optical["time"])
    max_mag = np.max(optical["mag"].to_numpy() + offset * (len(bands) - 1))
    min_mag = np.min(optical["mag"])

    for j, band in enumerate(bands):
        # Use pandas to select the points that correspond to the desired filter.

        # Use pandas to select the points that are upper limits.
        # Upper limits are represented by a 1 in the mag_limit column.
        upper_limits = optical.loc[
            (optical["band"] == band) & (optical["mag_limit"] == 1)
        ]["mag"]
        limit_times = optical.loc[
            (optical["band"] == band) & (optical["mag_limit"] == 1)
        ]["time"]

        # Use pandas to select the errors on the non-upper-limit points
        errors = optical.loc[(optical["band"] == band) & (optical["mag_limit"] != 1)][
            "dmag"
        ]

        # Use pandas to select the observation times and values.
        observations = optical.loc[
            (optical["band"] == band) & (optical["mag_limit"] != 1)
        ]["mag"]
        obs_times = optical.loc[
            (optical["band"] == band) & (optical["mag_limit"] != 1)
        ]["time"]

        # Plotting
        plt.plot(
            obs_times,
            observations + offset * j,
            label=str(band) + "+" + str(j * offset),
            marker="o",
            linestyle="",
            color=colours[j % 7],
            fillstyle=fills[j % 2],
        )
        plt.errorbar(
            obs_times,
            observations + offset * j,
            errors,
            linestyle="",
            color=colours[j % 7],
            marker="",
        )
        plt.plot(
            limit_times,
            upper_limits + offset * j,
            marker="v",
            linestyle="",
            color=colours[j % 7],
            fillstyle=fills[j % 2],
        )

    # Make it look good
    plt.xlabel("Time since GRB [days]")
    plt.xscale("log")
    plt.ylabel("Magnitude")
    plt.legend()
    plt.xlim([0.6 * (min_time), max_time + (5) * max_time])
    plt.ylim([max_mag + 0.5, min_mag - 0.5])
    plt.tick_params(which="minor", axis="x", direction="in")
    plt.tick_params(which="major", axis="x", direction="in")
    plt.tick_params(which="major", axis="y", direction="in")

    # save this pyplot into a BytesIO string
    byte_io = io.BytesIO()
    plt.savefig(byte_io, format="pdf")
    byte_io.seek(0)
    plt.close()
    return byte_io


def plot_radio(event):
    # Select the radio master file and import it.
    radio = pd.read_csv(
        os.path.join(
            app.root_path, "static/SourceData/", event, event + "_Radio_Master.txt"
        ),
        sep="\t",
    )

    # Select the frequency bands used
    freqs = list(set(list(radio["freq"])))

    # Choose colours for the plots
    colours = [
        "#D81B60",
        "#1E88E5",
        "#FFC107",
        "#004D40",
        "#6661B9",
        "#9F48E1",
        "#444297",
    ]
    fillstyles = ["none", "full"]

    # Make sure all fluxes are in mircoJy
    radio["flux_density"] = np.where(
        radio["flux_density_unit"] == "milliJy",
        radio["flux_density"] * 1000,
        radio["flux_density"],
    )
    radio["dflux_density"] = np.where(
        radio["flux_density_unit"] == "milliJy",
        radio["dflux_density"] * 1000,
        radio["dflux_density"],
    )
    radio["flux_density"] = np.where(
        radio["flux_density_unit"] == "Jy",
        radio["flux_density"] * 1000000,
        radio["flux_density"],
    )
    radio["dflux_density"] = np.where(
        radio["flux_density_unit"] == "Jy",
        radio["dflux_density"] * 1000000,
        radio["dflux_density"],
    )

    for j, freq in enumerate(freqs):
        # Use pandas to select the points that correspond to the desired frequency range.

        # Use pandas to select the points that are upper limits.
        # Upper limits are represented by a 1 in the flux_density_limit column.
        upper_limits = radio.loc[
            (radio["freq"] == freq) & (radio["flux_density_limit"] == 1)
        ]["flux_density"]
        limit_times = radio.loc[
            (radio["freq"] == freq) & (radio["flux_density_limit"] == 1)
        ]["time"]

        # Use pandas to select the errors on the non-upper-limit points
        errors = radio.loc[
            (radio["freq"] == freq) & (radio["flux_density_limit"] != 1)
        ]["dflux_density"]

        # Use pandas to select the observation times and values.
        observations = radio.loc[
            (radio["freq"] == freq) & (radio["flux_density_limit"] != 1)
        ]["flux_density"]
        obs_times = radio.loc[
            (radio["freq"] == freq) & (radio["flux_density_limit"] != 1)
        ]["time"]

        # Plotting
        plt.plot(
            obs_times,
            observations,
            label=str(freq) + "GHz",
            marker="o",
            linestyle="",
            color=colours[j % 7],
            fillstyle=fillstyles[j % 2],
        )
        plt.errorbar(
            obs_times,
            observations,
            errors,
            linestyle="",
            color=colours[j % 7],
            marker="",
        )
        plt.plot(
            limit_times,
            upper_limits,
            marker="v",
            linestyle="",
            color=colours[j % 7],
            fillstyle=fillstyles[j % 2],
        )

    # Make it look good.
    plt.xlabel("Time since GRB [days]")
    plt.xscale("log")
    plt.ylabel("Flux density [μJy]")
    plt.yscale("log")
    plt.legend()
    plt.tick_params(which="minor", axis="x", direction="in")
    plt.tick_params(which="major", axis="x", direction="in")
    plt.tick_params(which="major", axis="y", direction="in")

    # save this pyplot into a BytesIO string
    byte_io = io.BytesIO()
    plt.savefig(byte_io, format="pdf")
    byte_io.seek(0)
    plt.close()
    return byte_io


@api.route("/plotting/events_<events>+waverange_<waveranges>")
class Plotting(Resource):
    def get(self, waveranges, events):
        # Convert the string to a list
        waverange_list = ast.literal_eval("[" + waveranges + "]")
        event_list = ast.literal_eval("[" + events + "]")

        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as zf:
            for event in event_list:
                for waverange in waverange_list:
                    if waverange == "Optical":
                        if exists(
                            os.path.join(
                                app.root_path,
                                "static/SourceData/",
                                event,
                                event + "_Optical_Master.txt",
                            )
                        ):
                            optical_io = plot_optical(event)
                            zf.writestr(
                                event + "_" + waverange + ".pdf", optical_io.getvalue()
                            )
                    elif waverange == "Radio":
                        if exists(
                            os.path.join(
                                app.root_path,
                                "static/SourceData/",
                                event,
                                event + "_Radio_Master.txt",
                            )
                        ):
                            radio_io = plot_radio(event)
                            zf.writestr(
                                event + "_" + waverange + ".pdf", radio_io.getvalue()
                            )
        stream.seek(0)

        return send_file(stream, as_attachment=True, download_name="plots.zip")


# The homepage and its location


@app.route("/", methods=["POST", "GET"])
def home():
    # Connect to db
    conn = get_db_connection()

    # Ok new plan
    # Going to give it a go with the UNION and INTERSECT commands
    initial_query = f"SELECT GRB, SNe, GROUP_CONCAT(e_iso), GROUP_CONCAT(z), GROUP_CONCAT(T90), GROUP_CONCAT(ej_m), GROUP_CONCAT(ni_m), GROUP_CONCAT(E_p), GROUP_CONCAT(e_k) FROM SQLDataGRBSNe GROUP BY GRB, SNe ORDER BY GRB, SNe;"
    data = conn.execute(initial_query).fetchall()

    numeric = np.zeros(len(data))
    for i, row in enumerate(data):
        if row[1] != None:
            if row[1][:4].isnumeric():
                numeric[i] = 1

    form = SearchForm(request.form)

    if request.method == "POST":
        event_id = form.object_name.data
        print(event_id, sne)
        if str(event_id)[2:] in sne or str(event_id) in sne:  # if they search an SN
            event_id = event_id_maker(event_id)
            return redirect(url_for("event", event_id=event_id))
        elif str(event_id)[3:] in grbs:  # if they search an GRB
            event_id = event_id_maker(event_id)
            return redirect(url_for("event", event_id=event_id))
        else:
            flash("This object is not in our database.")
            return render_template("home.html", form=form, data=data, numerics=numeric)

    return render_template("home.html", form=form, data=data, numerics=numeric)


@app.route("/plot/e_iso")
def graph_data_grabber():
    conn = get_db_connection()

    # E_iso data, one value per GRB
    data = conn.execute("SELECT * FROM SQLDataGRBSNe WHERE GRB IS NOT NULL").fetchall()

    # Data for the graphs, remove the duplicates
    e_iso_photometric = []
    e_iso_spectroscopic = []
    grb_name = "start"

    for i in data:
        if i["e_iso"] != None and ">" not in i["e_iso"]:
            if i["GRB"] != grb_name and i["SNe"] != None:
                grb_name = i["GRB"]
                e_iso_spectroscopic.append(float(i["e_iso"]))

            elif i["GRB"] != grb_name and i["SNe"] == None:
                grb_name = i["GRB"]
                e_iso_photometric.append(float(i["e_iso"]))

    e_iso = e_iso_photometric + e_iso_spectroscopic

    conn.close()
    # Do graphing
    # E_iso plot

    fig = Figure()
    ax = fig.subplots()
    ax.hist(np.log10(e_iso), color="green", alpha=0.5)
    ax.set_xlabel("E$_{iso}$ (ergs)")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


@app.route("/plot/z")
def z_plotter():
    conn = get_db_connection()

    # E_iso data, one value per GRB
    data = conn.execute(
        "SELECT * FROM SQLDataGRBSNe WHERE GRB IS NOT NULL AND PrimarySources!='PRIVATE COM.'"
    ).fetchall()

    # Data for the graphs, remove the duplicates
    z_photometric = []
    z_spectroscopic = []
    grb_name = "start"

    for i in data:
        if i["z"] != None:
            if i["GRB"] != grb_name and i["SNe"] != None:
                grb_name = i["GRB"]
                z_spectroscopic.append(float(i["z"]))

            elif i["GRB"] != grb_name and i["SNe"] == None:
                grb_name = i["GRB"]
                z_photometric.append(float(i["z"]))

    conn.close()
    # Do graphing
    # E_iso plot

    fig = Figure()
    ax = fig.subplots()
    ax.hist(
        z_photometric,
        label="Photometric SN",
        alpha=0.5,
        edgecolor="black",
        color="green",
        bins=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
    )
    ax.hist(
        z_spectroscopic,
        label="Spectroscopic SN",
        alpha=0.5,
        edgecolor="black",
        color="purple",
        bins=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
    )
    ax.legend()
    ax.set_xlabel("Redshift")
    ax.set_ylabel("Frequency")

    canvas = FigureCanvas(fig)
    output = io.BytesIO()
    canvas.print_png(output)
    response = make_response(output.getvalue())
    response.mimetype = "image/png"
    return response


# References
# Primary (from all 3 tables)
with open("static/citations/citations.json") as file:
    dict_refs = json.load(file)

# Secondary
with open("static/citations/citations2.json") as file2:
    dict_refs2 = json.load(file2)

# ADS Downloaded data citations
with open("static/citations/citations(ADSdatadownloads).json") as file3:
    dict_refs3 = json.load(file3)

# Be able to select the GRBs by their names and go
# To a specific page, it also plots the XRT data


@app.route("/<event_id>")
def event(event_id):
    event, radec, peakmag = get_post(event_id)
    if len(event) == 0:
        abort(404)

    ######################################################
    ########### Referencing for table data ###############
    ######################################################

    # Find out how many of the references are needed
    needed_dict = {}
    event_nos = []
    event_refs = []
    for i in range(len(event)):
        if event[i]["PrimarySources"] != None:

            # If its not in the list save the citation and the number.
            if event[i]["PrimarySources"] not in list(needed_dict.keys()):
                needed_dict[event[i]["PrimarySources"]] = dict_refs[
                    event[i]["PrimarySources"]
                ]
                event_nos.append(
                    list(needed_dict.keys()).index(event[i]["PrimarySources"]) + 1
                )
                event_refs.append(event[i]["PrimarySources"])

            # If its already in the list theres no need to cite it again we just need the right number.
            else:
                event_nos.append(
                    list(needed_dict.keys()).index(event[i]["PrimarySources"]) + 1
                )

        elif event[i]["SecondarySources"] != None:
            # If its not in the list save the citation and the number.
            if radec[i]["source"] not in list(needed_dict.keys()):
                needed_dict[event[i]["SecondarySources"]] = dict_refs2[
                    event[i]["SecondarySources"]
                ]
                event_nos.append(
                    list(needed_dict.keys()).index(event[i]["SecondarySources"]) + 1
                )
                event_refs.append(event[i]["SecondarySources"])

            # If its already in the list theres no need to cite it again we just need the right number.
            else:
                event_nos.append(
                    list(needed_dict.keys()).index(event[i]["SecondarySources"]) + 1
                )

    # Add the radec swift stuff to the master dictionary of references for this event.
    radec_refs = []
    radec_nos = []

    for i in range(len(radec)):
        if radec[i]["source"] != None:

            # If its not in the list save the citation and the number.
            if radec[i]["source"] not in list(needed_dict.keys()):
                needed_dict[radec[i]["source"]] = dict_refs[radec[i]["source"]]
                radec_nos.append(list(needed_dict.keys()).index(radec[i]["source"]) + 1)
                radec_refs.append(radec[i]["source"])

            # If its already in the list theres no need to cite it again we just need the right number.
            else:
                radec_nos.append(list(needed_dict.keys()).index(radec[i]["source"]) + 1)

    # Get a list of all the bands we have peak times or mags for
    mag_bandlist = []
    ptime_bandlist = []
    for i in range(len(peakmag)):
        if peakmag[i]["band"] != None:
            if peakmag[i]["mag"] != None:
                mag_bandlist.append(peakmag[i]["band"])
            if peakmag[i]["time"] != None:
                ptime_bandlist.append(peakmag[i]["band"])

    # Add the peak times and mags references to the master dictionary of sources
    peakmag_refs = []
    peakmag_nos = []
    for i in range(len(peakmag)):
        if peakmag[i]["source"] != None:

            # If its not in the list save the citation and the number.
            if peakmag[i]["source"] not in list(needed_dict.keys()):
                needed_dict[peakmag[i]["source"]] = dict_refs[peakmag[i]["source"]]
                peakmag_nos.append(
                    list(needed_dict.keys()).index(peakmag[i]["source"]) + 1
                )
                peakmag_refs.append(peakmag[i]["source"])

            # If its already in the list theres no need to cite it again we just need the right number.
            else:
                peakmag_nos.append(
                    list(needed_dict.keys()).index(peakmag[i]["source"]) + 1
                )

    ######################################################################################
    ############# DATA FOR THE PLOTS#######################################################
    ######################################################################################

    # The time of the GRB
    if radec[0]["trigtime"] != None:
        grb_time = radec[0]["trigtime"]
    else:
        grb_time = "00:00:00"

    grb_time_str = 0

    # For the plot x axis time
    if radec[0]["grb_id"] != None:

        if int(str(radec[0]["grb_id"])[:2]) > 50 and radec[0]["grb_id"] != None:
            grb_time_str = (
                "19"
                + str(radec[0]["grb_id"])[:2]
                + "-"
                + str(radec[0]["grb_id"])[2:4]
                + "-"
                + str(radec[0]["grb_id"])[4:6]
                + " "
                + grb_time
            )
            grb_time_iso = (
                "19"
                + str(radec[0]["grb_id"])[:2]
                + "-"
                + str(radec[0]["grb_id"])[2:4]
                + "-"
                + str(radec[0]["grb_id"])[4:6]
                + "T"
                + grb_time
            )

        elif int(str(radec[0]["grb_id"])[:2]) <= 50 and radec[0]["grb_id"] != None:
            grb_time_str = (
                "20"
                + str(radec[0]["grb_id"])[:2]
                + "-"
                + str(radec[0]["grb_id"])[2:4]
                + "-"
                + str(radec[0]["grb_id"])[4:6]
                + " "
                + grb_time
            )
            grb_time_iso = (
                "20"
                + str(radec[0]["grb_id"])[:2]
                + "-"
                + str(radec[0]["grb_id"])[2:4]
                + "-"
                + str(radec[0]["grb_id"])[4:6]
                + "T"
                + grb_time
            )

    else:
        if grb_time == "00:00:00":
            grb_time_str = "1970-01-01 00:00:00"
            grb_time_iso = "1970-01-01T00:00:00"
        else:
            grb_time_str_split = radec[0]["trigtime"].split("T")
            grb_time_str = grb_time_str_split[0] + " " + grb_time_str_split[1]
            grb_time_iso = str(radec[0]["trigtime"])

    # Convert to MJD
    # make the isotime object
    t = Time(grb_time_iso, format="isot", scale="utc")
    grb_time_mjd = t.mjd

    ######################################################################################
    ##### X--RAYS##########################################################################
    ######################################################################################
    # Tracker variable to tell us whether theres any Xray data or not
    track = 0

    # create a new plot with a title and axis labels
    xray = figure(
        title="X-ray",
        toolbar_location="right",
        y_axis_type="log",
        x_axis_type="log",
        margin=5,
        aspect_ratio=16 / 9,
        max_width=1000,
    )

    legend_it = []
    #################################
    # Swift data ####################
    #################################
    # Swift references
    xray_refs = []
    swift_reference_no = []

    # The swift xrtlc files.
    # Check if the xrtlc file exists.
    if exists(
        "static/SourceData/"
        + event_id
        + "/"
        + str(event_id.split("-")[0])
        + "xrtlc.txt"
    ):

        # Get the data from the lc file.
        data = pd.read_csv(
            "static/SourceData/"
            + event_id
            + "/"
            + str(event_id.split("-")[0])
            + "xrtlc.txt",
            header=0,
            delimiter="\t",
        )
        data.columns = [
            "time",
            "dt_pos",
            "dt_neg",
            "flux",
            "dflux_pos",
            "dflux_neg",
            "limit",
        ]

        track += 1

        with open("static/citations/swift_ads.json") as file3:
            swift_bursts = json.load(file3)
        for swift_reference in list(swift_bursts.keys()):
            if swift_reference not in list(needed_dict.keys()):
                needed_dict[swift_reference] = swift_bursts[swift_reference]
                xray_refs.append(swift_reference)
                swift_reference_no.append(
                    list(needed_dict.keys()).index(swift_reference) + 1
                )
            else:
                swift_reference_no.append(
                    list(needed_dict.keys()).index(swift_reference) + 1
                )

        # t, dt_pos, dt_neg, flux, dflux_pos, dflux_neg, limit = data
        # Add the references
        data["sources"] = [swift_reference_no] * len(data["time"])

        # Add units
        data["units"] = ["erg/cm^2/sec"] * len(data["time"])

        # Add the instrument
        data["instrument"] = ["Swift XRT"] * len(data["time"])

        # Convert the string representing whether its a limit or not to string
        data["stringlimit"] = data["limit"].astype(str)

        # Fix the error columns so they work on log plots with whisker
        data["error"] = list(
            zip(data["flux"] + data["dflux_neg"], data["flux"] + data["dflux_pos"])
        )
        data["e_locs"] = list(zip(data["time"], data["time"]))

        data["terror"] = list(
            zip(data["time"] + data["dt_neg"], data["time"] + data["dt_pos"])
        )
        data["te_locs"] = list(zip(data["flux"], data["flux"]))

        xray_source = ColumnDataSource(data)

        types = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        marks = [
            "circle",
            "inverted_triangle",
            "triangle",
            "circle",
            "inverted_triangle",
            "triangle",
            "circle",
            "inverted_triangle",
            "triangle",
        ]

        # add a line renderer with legend and line thickness
        a = xray.multi_line(
            "e_locs",
            "error",
            source=xray_source,
            color="orange",
            line_width=2,
            muted_color="gray",
            muted_alpha=0.05,
        )
        b = xray.multi_line(
            "terror",
            "te_locs",
            source=xray_source,
            color="orange",
            line_width=2,
            muted_color="gray",
            muted_alpha=0.05,
        )
        c = xray.scatter(
            "time",
            "flux",
            source=xray_source,
            size=7,
            color="orange",
            fill_color="orange",
            marker=factor_mark("stringlimit", marks, types),
            muted_color="gray",
            muted_alpha=0.05,
        )
        legend_it.append(("0.3-10keV  ", [a, b, c]))
        # Tooltips of what will display in the hover mode
        # Format the tooltip

        tooltips = [
            ("Time", "@time"),
            ("Flux", "@flux"),
            ("Instrument", "@instrument"),
            ("Source", "@sources"),
            ("Unit", "@units"),
        ]

        # Add the HoverTool to the figure
        xray.add_tools(HoverTool(tooltips=tooltips))

    #################################
    # ADS data ######################
    #################################

    # Check if the xray master file exists yet.
    if exists(
        "static/SourceData/" + str(event_id) + "/" + str(event_id) + "_Xray_Master.txt"
    ):
        # Add 1 to track variable if openSN had data
        track += 1

        # Get the files that were downloaded from the ADS
        xray_df = pd.read_csv(
            "static/SourceData/"
            + str(event_id)
            + "/"
            + str(event_id)
            + "_Xray_Master.txt",
            sep="\t",
        )

        ####### References ##########
        # Get the list of unique references
        x_refs = xray_df["reference"]

        # Sub list of the indices for the optical data from the ADS
        xray_source_indices_sub = []
        for ref in x_refs:
            if ref in needed_dict.keys():
                xray_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

            else:
                # Add to the needed_dict
                needed_dict[ref] = {
                    "names": dict_refs3[ref]["names"],
                    "year": dict_refs3[ref]["year"],
                }

                # Save the optical ref to use as a key in event html when accessing the reference.
                xray_refs.append(ref)

                xray_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

        # Add the lists of indices to the DF
        xray_df["sources"] = xray_source_indices_sub

        ####### Plot Data ###########
        # Select colours for the data
        colors = d3["Category20"][20]

        # List of the energy ranges
        energy_ranges = list(set(list(xray_df["energy_range"])))

        # Identify any upper limits
        xray_df["flux_limit_str"] = xray_df["flux_limit"].astype(str)

        # Create the error columns that bokeh wants
        # Errors on fluxes
        xray_error_df = xray_df[["time", "flux", "dflux", "energy_range"]].copy()
        xray_error_df = xray_error_df[~xray_error_df["dflux"].isnull()]
        xray_error_df["dfluxes"] = list(
            zip(
                xray_error_df["flux"].astype(float)
                - xray_error_df["dflux"].astype(float),
                xray_error_df["flux"].astype(float)
                + xray_error_df["dflux"].astype(float),
            )
        )
        xray_error_df["dflux_locs"] = list(
            zip(xray_error_df["time"], xray_error_df["time"])
        )

        for k, energy_range in enumerate(energy_ranges):
            xray_data = xray_df.loc[xray_df["energy_range"] == energy_range]
            xray_error = xray_error_df.loc[
                xray_error_df["energy_range"] == energy_range
            ]
            # Create a cds
            xray_cds = ColumnDataSource(xray_data)

            # Create a cds for errors
            xray_error_cds = ColumnDataSource(xray_error)

            # Plotting
            types2 = ["-1", "0", "1"]
            marks2 = ["triangle", "circle", "inverted_triangle"]
            b = xray.multi_line(
                "dflux_locs",
                "dfluxes",
                source=xray_error_cds,
                color=colors[int(k % 20)],
                line_width=2,
                muted_color="gray",
                muted_alpha=0.05,
            )
            c = xray.scatter(
                "time",
                "flux",
                source=xray_cds,
                size=7,
                color=colors[int(k % 20)],
                muted_color="gray",
                muted_alpha=0.05,
                fill_color=colors[int(k % 20)],
                marker=factor_mark("flux_limit_str", marks2, types2),
            )
            legend_it.append((energy_range + "  ", [c, b]))

        # Tooltips of what will display in the hover mode
        # Format the tooltip

        tooltips = [
            ("Time", "@time"),
            ("Flux", "@flux"),
            ("Instrument", "@instrument"),
            ("Source", "@sources"),
            ("Unit", "@flux_unit"),
        ]

        # Add the HoverTool to the figure
        xray.add_tools(HoverTool(tooltips=tooltips))

    # Aesthetics
    xray.title.text_font_size = "20pt"
    xray.title.text_color = "black"
    xray.title.align = "center"

    # Axis font size
    xray.yaxis.axis_label_text_font_size = "16pt"
    xray.xaxis.axis_label_text_font_size = "16pt"

    # Font Color
    xray.xaxis.axis_label_text_color = "black"
    xray.xaxis.major_label_text_color = "black"

    xray.yaxis.axis_label_text_color = "black"
    xray.yaxis.major_label_text_color = "black"

    # Tick colors
    xray.xaxis.major_tick_line_color = "black"
    xray.yaxis.major_tick_line_color = "black"

    xray.xaxis.minor_tick_line_color = "black"
    xray.yaxis.minor_tick_line_color = "black"

    # Axis labels
    xray.xaxis.axis_label = "Time [sec] since " + grb_time_str
    xray.yaxis.axis_label = "Flux [erg/cm^2/sec]"

    # Axis Colors
    xray.xaxis.axis_line_color = "black"
    xray.yaxis.axis_line_color = "black"

    # Make ticks larger
    xray.xaxis.major_label_text_font_size = "16pt"
    xray.yaxis.major_label_text_font_size = "16pt"

    xray.background_fill_color = "white"
    xray.border_fill_color = "white"

    # Allow user to mute individual bands by clicking the legend
    num = 10
    for i in range(math.ceil(len(legend_it) / num)):
        if i + 1 < len(legend_it) / num:
            legend2 = Legend(items=legend_it[i * num : i * num + num])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            xray.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"
        else:
            legend2 = Legend(items=legend_it[i * num : i * num + len(legend_it)])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            xray.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"

    # If track is still 0 print nodata
    if track == 0:
        # Set a range so we can always centre the nodata for the spectra plot
        xray.y_range = Range1d(5e-15, 5e-9)
        xray.x_range = Range1d(1, 150000)

        nodata_warn = Label(
            x=10,
            y=1.3e-12,
            x_units="data",
            y_units="data",
            text=processing_tag(event_id, "Xray"),
            render_mode="css",
            text_font_size="50pt",
            border_line_color="grey",
            border_line_alpha=0,
            text_alpha=0.2,
            background_fill_alpha=1.0,
            text_color="black",
        )
        xray.add_layout(nodata_warn)

    ######################################################################################
    ##### OPTICAL##########################################################################
    ######################################################################################
    # Tracker variable to tell us whether theres been either OpenSN data or ADS data.
    track = 0

    t0_utc = "0"

    optical = figure(
        title="Optical (GRB+SN)",
        toolbar_location="right",
        x_axis_type="log",
        margin=5,
        aspect_ratio=16 / 9,
        max_width=1000,
    )

    ####### References #############
    optical_refs = []  # Has to be outside the loop so it wont crash for non SN pages

    ################################
    ######## Open SN ###############
    ################################
    legend_it = []
    if exists("./static/SourceData/" + str(event_id) + "/" + "OpenSNPhotometry.csv"):
        # Add 1 to track variable if openSN had data
        track += 1

        # This is supposed to show the number to be assigned to a particular source.
        optical_source_indices = []
        # Extract and plot the optical photometry data from the photometry file for each SN

        data = pd.read_csv(
            "./static/SourceData/" + str(event_id) + "/" + "OpenSNPhotometry.csv"
        )
        if data.empty == False:

            # Indexing the sources
            for dictionaries in data["refs"]:
                dictionaries = ast.literal_eval(dictionaries)
                # Sub list of the indices for each reference
                optical_source_indices_sub = []
                for reference in dictionaries:
                    # Check if its already in the needed_dict
                    if reference["url"] in needed_dict.keys():
                        optical_source_indices_sub.append(
                            (list(needed_dict.keys()).index(reference["url"]) + 1)
                        )

                    else:
                        # Extract the names and the years from the citation
                        p = list(str(reference["name"]).split("("))

                        # Account for non ads references
                        if len(p) > 1:
                            names = p[0][:-1]
                            year = p[1][:-1]

                            # Add to the needed_dict
                            needed_dict[reference["url"]] = {
                                "names": names,
                                "year": year,
                            }

                        else:
                            names = reference["name"]
                            # Add to the needed_dict
                            needed_dict[reference["url"]] = {"names": names, "year": ""}

                        # Save the optical ref to use as a key in event html when accessing the reference.
                        optical_refs.append(reference["url"])
                        # Append the number (now only needed for the graph)
                        optical_source_indices_sub.append(
                            (list(needed_dict.keys()).index(reference["url"]) + 1)
                        )

                # Get the numbering for the sources to display in the right order on the plots
                if len(optical_source_indices_sub) > 1:
                    optical_source_indices.append(np.sort(optical_source_indices_sub))
                else:
                    optical_source_indices.append(optical_source_indices_sub)

            # Add the lists of indices to the DF
            data["indices"] = optical_source_indices

            # Splitting the data by band for plotting purposes
            bands = set(data["band"].astype(str))

            color = Category20_20.__iter__()
            for j in bands:

                if "nan" in str(j).lower():

                    # New df of just points without a band name (ie nan)
                    new_df = data.loc[data["band"].isna()]

                    # Say that the band is unknown
                    new_df["band"] = ["Unknown"] * len(new_df["band"])

                    # Band label for the legend
                    band_label = "Unknown"

                else:
                    # Create a df with just the band j
                    new_df = data.loc[data["band"] == j]

                    # Band label for the legend
                    band_label = str(j)

                # Convert the times from MJD to UTC, then subtract the first timestamp
                mjd_time = np.array(new_df["time"])
                t_after_t0 = np.zeros(len(new_df["time"]))
                t0 = min(mjd_time)  # earliest mjd in time
                t0_utc = Time(t0, format="mjd").utc.iso

                for k in range(len(mjd_time)):
                    t_after_t0[k] = float(mjd_time[k]) - float(grb_time_mjd)

                # Add this to the df in the position time used to be in.
                new_df["time_since"] = t_after_t0

                # Errors on magnitudes
                optical_error_df = new_df[
                    ["time_since", "magnitude", "e_magnitude"]
                ].copy()
                optical_error_df = optical_error_df[
                    ~optical_error_df["e_magnitude"].isnull()
                ]
                optical_error_df["dmags"] = list(
                    zip(
                        optical_error_df["magnitude"] - optical_error_df["e_magnitude"],
                        optical_error_df["magnitude"] + optical_error_df["e_magnitude"],
                    )
                )
                optical_error_df["dmag_locs"] = list(
                    zip(optical_error_df["time_since"], optical_error_df["time_since"])
                )

                optical_error = ColumnDataSource(optical_error_df)
                optical_data = ColumnDataSource(new_df)

                # New color
                col = next(color)
                b = optical.multi_line(
                    "dmag_locs",
                    "dmags",
                    source=optical_error,
                    muted_color="gray",
                    muted_alpha=0.05,
                    color=col,
                    line_color=col,
                    line_width=2,
                )
                c = optical.scatter(
                    "time_since",
                    "magnitude",
                    source=optical_data,
                    muted_color="gray",
                    muted_alpha=0.05,
                    size=7,
                    fill_color=col,
                    color=col,
                )
                legend_it.append((j + "  ", [c, b]))

                # Tooltips of what will display in the hover mode
                # Format the tooltip
                # Tooltips of what will display in the hover mode
                # Format the tooltip
                tooltips = [
                    ("Time", "@time_since"),
                    ("Magnitude", "@magnitude"),
                    ("Band", "@band"),
                    ("Source", "@indices"),
                    ("Unit", "@mag_unit"),
                ]

                # Add the HoverTool to the figure
                optical.add_tools(HoverTool(tooltips=tooltips))

    #################################
    # ADS data ######################
    #################################
    # Check if the optical master file exists yet.
    if exists(
        "static/SourceData/"
        + str(event_id)
        + "/"
        + str(event_id)
        + "_Optical_Master.txt"
    ):
        # Add 1 to track variable if openSN had data
        track += 1

        # Get the files that were downloaded from the ADS
        optical_df = pd.read_csv(
            "static/SourceData/"
            + str(event_id)
            + "/"
            + str(event_id)
            + "_Optical_Master.txt",
            sep="\t",
        )

        ####### References ##########
        # Get the list of unique references
        op_refs = optical_df["reference"]

        # Sub list of the indices for the optical data from the ADS
        optical_source_indices_sub = []
        for ref in op_refs:
            if ref in needed_dict.keys():
                optical_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

            else:
                # Add to the needed_dict
                needed_dict[ref] = {
                    "names": dict_refs3[ref]["names"],
                    "year": dict_refs3[ref]["year"],
                }

                # Save the optical ref to use as a key in event html when accessing the reference.
                optical_refs.append(ref)

                optical_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

        # Add the lists of indices to the DF
        optical_df["indices"] = optical_source_indices_sub

        ####### Plot Data ###########

        # Set the string values for the bands
        optical_df["mag_limit_str"] = optical_df["mag_limit"].astype(str)

        # Select colours for the data
        colors = d3["Category20"][20]

        # Create the error columns that bokeh wants
        # Errors on flux densities
        optical_error_df = optical_df[["time", "mag", "dmag", "band"]].copy()
        optical_error_df = optical_error_df[~optical_error_df["dmag"].isnull()]
        optical_error_df["dmags"] = list(
            zip(
                optical_error_df["mag"].astype(float)
                - optical_error_df["dmag"].astype(float),
                optical_error_df["mag"].astype(float)
                + optical_error_df["dmag"].astype(float),
            )
        )
        optical_error_df["dmag_locs"] = list(
            zip(optical_error_df["time"], optical_error_df["time"])
        )

        # List all bands
        bands = list(set(list(optical_df["band"].astype(str))))

        for k, band in enumerate(bands):
            band_data = optical_df.loc[optical_df["band"] == band]
            band_error = optical_error_df.loc[optical_error_df["band"] == band]

            # Create a cds
            optical_cds = ColumnDataSource(band_data)

            # Create a cds for errors
            optical_error_cds = ColumnDataSource(band_error)

            # Plotting

            types2 = ["-1", "0", "1"]
            marks2 = ["triangle", "circle", "inverted_triangle"]
            b = optical.multi_line(
                "dmag_locs",
                "dmags",
                source=optical_error_cds,
                color=colors[int(k % 20)],
                line_width=2,
                muted_color="gray",
                muted_alpha=0.05,
            )
            if k < 20:
                c = optical.scatter(
                    "time",
                    "mag",
                    source=optical_cds,
                    size=7,
                    line_color=colors[int(k % 20)],
                    color=colors[int(k % 20)],
                    muted_color="gray",
                    muted_alpha=0.05,
                    fill_color=colors[int(k % 20)],
                    marker=factor_mark("mag_limit_str", marks2, types2),
                )
            else:
                c = optical.scatter(
                    "time",
                    "mag",
                    source=optical_cds,
                    size=7,
                    line_color=colors[int(k % 20)],
                    color=colors[int(k % 20)],
                    muted_color="gray",
                    muted_alpha=0.05,
                    fill_color="none",
                    marker=factor_mark("mag_limit_str", marks2, types2),
                )
            legend_it.append((band + "  ", [c, b]))
        # Tooltips of what will display in the hover mode
        # Format the tooltip
        # Tooltips of what will display in the hover mode
        # Format the tooltip
        tooltips = [
            ("Time", "@time"),
            ("Magnitude", "@mag"),
            ("Band", "@band"),
            ("Instrument", "@instrument"),
            ("Source", "@indices"),
            ("Unit", "@mag_unit"),
        ]

        # Add the HoverTool to the figure
        optical.add_tools(HoverTool(tooltips=tooltips))

    optical.y_range.flipped = True

    # Aesthetics

    # Title
    optical.title.text_font_size = "20pt"
    optical.title.text_color = "black"
    optical.title.align = "center"

    # Axis font size
    optical.yaxis.axis_label_text_font_size = "16pt"
    optical.xaxis.axis_label_text_font_size = "16pt"

    # Font Color
    optical.xaxis.axis_label_text_color = "black"
    optical.xaxis.major_label_text_color = "black"

    optical.yaxis.axis_label_text_color = "black"
    optical.yaxis.major_label_text_color = "black"

    # Tick colors
    optical.xaxis.major_tick_line_color = "black"
    optical.yaxis.major_tick_line_color = "black"

    optical.xaxis.minor_tick_line_color = "black"
    optical.yaxis.minor_tick_line_color = "black"

    # Axis labels
    if t0_utc == 0:
        optical.xaxis.axis_label = "Time [MJD]"
    else:
        optical.xaxis.axis_label = "Time [days] after: " + grb_time_str

    optical.yaxis.axis_label = "Apparent Magnitude"

    # Axis Colors
    optical.xaxis.axis_line_color = "black"
    optical.yaxis.axis_line_color = "black"

    # Allow user to mute individual bands by clicking the legend
    num = 20
    for i in range(math.ceil(len(legend_it) / num)):
        if i + 1 < len(legend_it) / num:
            legend2 = Legend(items=legend_it[i * num : i * num + num])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            optical.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"
        else:
            legend2 = Legend(items=legend_it[i * num : i * num + len(legend_it)])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            optical.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"

    # Make ticks larger
    optical.xaxis.major_label_text_font_size = "16pt"
    optical.yaxis.major_label_text_font_size = "16pt"

    optical.background_fill_color = "white"
    optical.border_fill_color = "white"

    # If track is still 0 print nodata/pending
    if track == 0:
        # Set a range so we can always centre the nodata for the spectra plot
        optical.y_range = Range1d(20, 17)
        optical.x_range = Range1d(1, 100)

        nodata_warn = Label(
            x=2,
            y=18.8,
            x_units="data",
            y_units="data",
            text=processing_tag(event_id, "Optical"),
            render_mode="css",
            text_font_size="50pt",
            border_line_color="grey",
            border_line_alpha=0,
            text_alpha=0.2,
            background_fill_alpha=1.0,
            text_color="black",
        )
        optical.add_layout(nodata_warn)

    ######################################################################################
    ##### RADIO############################################################################
    ######################################################################################
    radio = figure(
        title="Radio (GRB)",
        toolbar_location="right",
        y_axis_type="log",
        x_axis_type="log",
        margin=5,
        aspect_ratio=16 / 9,
        max_width=1000,
    )

    #################################
    # ADS data ######################
    #################################
    rad_refs = []
    legend_it = []
    # Check if the radio master file exists yet.
    if exists(
        "static/SourceData/" + str(event_id) + "/" + str(event_id) + "_Radio_Master.txt"
    ):

        # Get the files that were downloaded from the ADS
        radio_df = pd.read_csv(
            "static/SourceData/"
            + str(event_id)
            + "/"
            + str(event_id)
            + "_Radio_Master.txt",
            sep="\t",
        )

        ####### References ##########
        # Get the list of unique references
        radio_refs = radio_df["reference"]

        # Sub list of the indices for the radio data from the ADS
        radio_source_indices_sub = []
        for ref in radio_refs:
            if ref in needed_dict.keys():
                radio_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

            else:
                # Add to the needed_dict
                needed_dict[ref] = {
                    "names": dict_refs3[ref]["names"],
                    "year": dict_refs3[ref]["year"],
                }

                # Save the radio ref to use as a key in event html when accessing the reference.
                rad_refs.append(ref)

                radio_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

        # List all the frequencies.
        freqs = list(set(list(radio_df["freq"].astype(str))))

        # Add the lists of indices to the DF
        radio_df["indices"] = radio_source_indices_sub

        # Plot the radio data we have gathered.
        colors = d3["Category20"][20]

        # Get strings for the mapper functions
        radio_df["flux_density_limit_str"] = radio_df["flux_density_limit"].astype(str)
        radio_df["freq_str"] = radio_df["freq"].astype(str)

        radio_df["unit_col"] = (
            radio_df["freq"].astype(str) + " " + radio_df["freq_unit"].astype(str)
        )
        freq_unit = list(set(list(radio_df["unit_col"].astype(str))))

        # Get the units right
        radio_df["flux_density"] = radio_df["flux_density"].astype(float)

        if "dflux_density" in list(radio_df.keys()):
            radio_df["dflux_density"] = radio_df["dflux_density"].astype(float)
        else:
            radio_df["dflux_density"] = np.ones(len(radio_df["flux_density"])) * np.nan

        for i in range(len(radio_df["flux_density_unit"])):
            # Convert microJy to millyJy by dividing by 1000
            if radio_df["flux_density_unit"][i] == "microJy":
                radio_df["flux_density"][i] = radio_df["flux_density"][i] / 1000
                radio_df["dflux_density"][i] = radio_df["dflux_density"][i] / 1000

            # Convert Jy to millyJy by multiplying by 1000
            if radio_df["flux_density_unit"][i] == "Jy":
                radio_df["flux_density"][i] = radio_df["flux_density"][i] * 1000
                radio_df["dflux_density"][i] = radio_df["dflux_density"][i] * 1000

        # Errors on flux densities
        radio_error_df = radio_df[
            ["time", "flux_density", "dflux_density", "freq_str", "unit_col"]
        ].copy()
        radio_error_df = radio_error_df[~radio_error_df["dflux_density"].isnull()]
        radio_error_df["dfds"] = list(
            zip(
                radio_error_df["flux_density"] - radio_error_df["dflux_density"],
                radio_error_df["flux_density"] + radio_error_df["dflux_density"],
            )
        )
        radio_error_df["dfd_locs"] = list(
            zip(radio_error_df["time"], radio_error_df["time"])
        )

        for k, freq_unit in enumerate(freq_unit):
            freq_data = radio_df.loc[radio_df["unit_col"] == freq_unit]
            freq_error = radio_error_df.loc[radio_error_df["unit_col"] == freq_unit]

            # Create a column data source object to make some of the plotting easier.
            radio_cds = ColumnDataSource(freq_data)
            radio_error = ColumnDataSource(freq_error)

            # Setting up to map the upper limits to different symbols.
            types2 = ["-1", "0", "1"]
            marks2 = ["triangle", "circle", "inverted_triangle"]

            # Plot the data and the error
            b = radio.multi_line(
                "dfd_locs",
                "dfds",
                source=radio_error,
                color=colors[int(k % 20)],
                line_width=2,
                muted_color="gray",
                muted_alpha=0.05,
            )

            if k < 20:
                c = radio.scatter(
                    "time",
                    "flux_density",
                    source=radio_cds,
                    size=7,
                    line_color=colors[int(k % 20)],
                    color=colors[int(k % 20)],
                    muted_color="gray",
                    muted_alpha=0.05,
                    fill_color=colors[int(k % 20)],
                    marker=factor_mark("flux_density_limit_str", marks2, types2),
                )
            else:
                c = radio.scatter(
                    "time",
                    "flux_density",
                    source=radio_cds,
                    size=7,
                    line_color=colors[int(k % 20)],
                    color=colors[int(k % 20)],
                    muted_color="gray",
                    muted_alpha=0.05,
                    fill_color="none",
                    marker=factor_mark("flux_density_limit_str", marks2, types2),
                )
            legend_it.append((freq_unit + "  ", [c, b]))

        # Tooltips of what will display in the hover mode
        # Format the tooltip
        # Tooltips of what will display in the hover mode
        # Format the tooltip
        tooltips = [
            ("Time", "@time"),
            ("Freq", "@freq"),
            ("Flux Density", "@flux_density"),
            ("Instrument", "@instrument"),
            ("Source", "@indices"),
        ]

        # Add the HoverTool to the figure
        radio.add_tools(HoverTool(tooltips=tooltips))

    else:
        # Set a range so we can always centre the nodata for the spectra plot
        radio.x_range = Range1d(1, 10)
        radio.y_range = Range1d(1, 3)

        nodata_warn = Label(
            x=1.7,
            y=1.55,
            x_units="data",
            y_units="data",
            text=processing_tag(event_id, "Radio"),
            render_mode="css",
            text_font_size="50pt",
            border_line_color="grey",
            border_line_alpha=0,
            text_alpha=0.2,
            background_fill_alpha=1.0,
            text_color="black",
        )
        radio.add_layout(nodata_warn)

    # Aesthetics

    # Title
    radio.title.text_font_size = "20pt"
    radio.title.text_color = "black"
    radio.title.align = "center"
    # Axis font size
    radio.yaxis.axis_label_text_font_size = "16pt"
    radio.xaxis.axis_label_text_font_size = "16pt"

    # Font Color
    radio.xaxis.axis_label_text_color = "black"
    radio.xaxis.major_label_text_color = "black"

    radio.yaxis.axis_label_text_color = "black"
    radio.yaxis.major_label_text_color = "black"

    # Tick colors
    radio.xaxis.major_tick_line_color = "black"
    radio.yaxis.major_tick_line_color = "black"

    radio.xaxis.minor_tick_line_color = "black"
    radio.yaxis.minor_tick_line_color = "black"

    # Axis labels
    radio.xaxis.axis_label = "Time [days] after " + grb_time_str
    radio.yaxis.axis_label = "Flux Density [mJy]"

    # Axis Colors
    radio.xaxis.axis_line_color = "black"
    radio.yaxis.axis_line_color = "black"

    # Make ticks larger
    radio.xaxis.major_label_text_font_size = "16pt"
    radio.yaxis.major_label_text_font_size = "16pt"

    radio.background_fill_color = "white"
    radio.border_fill_color = "white"

    # Legend
    # Allow user to mute individual bands by clicking the legend
    num = 20
    for i in range(math.ceil(len(legend_it) / num)):
        if i + 1 < len(legend_it) / num:
            legend2 = Legend(items=legend_it[i * num : i * num + num])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            radio.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"
        else:
            legend2 = Legend(items=legend_it[i * num : i * num + len(legend_it)])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            radio.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"

    ######################################################################################
    ##### SNe SPECTRA######################################################################
    ######################################################################################
    legend_it = []

    # Selection tools we want to display
    select_tools = ["box_zoom", "pan", "wheel_zoom", "save", "reset"]

    # Figure
    spectrum = figure(
        title="Spectrum (SN)",
        toolbar_location="right",
        tools=select_tools,
        margin=5,
        aspect_ratio=1,
        max_width=1000,
    )

    # Blank tooltips
    tooltips = []

    # Spectra sources (outside loop so as not to crash pages when no SN)
    spec_refs = []

    max_spec = [10]
    min_spec = [0]

    # Check for json files
    if exists("static/SourceData/" + str(event_id) + "/" + "OpenSNSpectra0.json"):

        # Access the data in the files for the SNe Spectra
        path = "./static/SourceData/" + str(event_id) + "/"
        files = glob.glob(path + "/*.json")

        # Colormap to be used - 45 is the max number of spectra im expecting for a single event
        color = viridis(len(files))

        if len(files) != 0:
            max_spec = np.zeros(len(files))
            min_spec = np.zeros(len(files))

        for i in range(len(files)):
            with open(files[i]) as json_file:
                data_i = json.load(json_file)

                # Split the data into two lists, one wavelengths and one flux
                wavelength, flux = zip(
                    *data_i["SN" + str(event[0]["SNe"])]["spectra"]["data"]
                )

                wavelength = np.array(wavelength, dtype=np.float32)
                flux = np.array(flux, dtype=np.float32)

                # Convert to rest wavelength if necessary
                redshift = []
                for o in range(len(event)):
                    if event[o]["z"] is not None:
                        redshift.append(float(event[o]["z"]))

                if "deredshifted" in list(
                    data_i["SN" + str(event[0]["SNe"])]["spectra"].keys()
                ):
                    if (
                        data_i["SN" + str(event[0]["SNe"])]["spectra"]["deredshifted"]
                        == "False"
                    ):
                        wavelength = wavelength / (1 + redshift[0])

                else:
                    wavelength = wavelength / (1 + redshift[0])

                # Scale the flux using the 5000A flux
                if max(wavelength) < 5000:
                    flux = flux / flux[-1]
                elif min(wavelength) > 5000:
                    flux = flux / flux[0]
                else:
                    flux = flux / (interp1d(wavelength, flux)(np.array([5000])))

                # Calculating the extent of the limits on the plots
                max_spec[i] = max(flux)
                min_spec[i] = min(flux)

                # Create a dictionary of the necessary info
                data_dict = {
                    "wavelength": wavelength,
                    "flux": flux,
                    "time": [data_i["SN" + str(event[0]["SNe"])]["spectra"]["time"]]
                    * len(wavelength),
                }

                ############ SOURCES ############
                sources = data_i["SN" + str(event[0]["SNe"])]["spectra"]["source"]

                # This is supposed to show the number to be assigned to a particular source.
                source_indices = []

                for k in range(len(sources)):
                    # Check if we are already using this reference for some of the data in the tables or for another spectrum
                    if sources[k]["url"] in needed_dict.keys():
                        source_indices.append(
                            list(needed_dict.keys()).index(sources[k]["url"]) + 1
                        )
                    else:

                        # Account for non ads references
                        # if the final digits look like a year
                        if (
                            "19" in sources[k]["name"][-4:-2]
                            or "20" in sources[k]["name"][-4:-2]
                        ):

                            # Add to the needed_dict
                            needed_dict[sources[k]["url"]] = {
                                "names": sources[k]["name"][:-4],
                                "year": sources[k]["name"][-4:],
                            }

                        else:
                            names = sources[k]["name"]
                            # Add to the needed_dict
                            needed_dict[sources[k]["url"]] = {
                                "names": names,
                                "year": "",
                            }

                        # Save the spectra ref to use as a key in event html when accessing the reference.
                        spec_refs.append(sources[k]["url"])

                        # Append the number (now only needed for the graph)
                        source_indices.append(
                            list(needed_dict.keys()).index(sources[k]["url"]) + 1
                        )

                # Convert the times from MJD to UTC, then subtract the first timestamp
                mjd_time = np.array(data_dict["time"])
                t_after_t0 = np.zeros(len(data_dict["time"]))
                t0 = min(mjd_time)  # earliest mjd in time
                t0_utc = Time(t0, format="mjd").utc.iso

                for k in range(len(mjd_time)):
                    t_after_t0[k] = float(mjd_time[k]) - float(grb_time_mjd)

                # Add this to the df in the position time used to be in.
                data_dict["time_since"] = t_after_t0

                data_dict["sources"] = [np.sort(source_indices)] * len(wavelength)

                #### UNITS #####
                data_dict["wave_unit"] = [
                    data_i["SN" + str(event[0]["SNe"])]["spectra"]["u_wavelengths"]
                ] * len(wavelength)
                data_dict["flux_unit"] = [
                    data_i["SN" + str(event[0]["SNe"])]["spectra"]["u_fluxes"]
                ] * len(wavelength)

                # Convert the dict to a column data object
                data_source = ColumnDataSource(data_dict)

                # Tooltips of what will display in the hover mode
                # Format the tooltip
                tooltips = [
                    ("Rest wavelength", "@wavelength{0}"),
                    ("Wavelength unit", "@wave_unit"),
                    ("Flux", "@flux"),
                    ("Flux unit", "@flux_unit"),
                    ("Time [days]", "@time_since"),
                    ("Source", "@sources"),
                ]

                # Legend label will be the elapsed time since the trigger for now
                c = spectrum.line(
                    "wavelength",
                    "flux",
                    source=data_source,
                    color=color[i],
                    muted_color="gray",
                    muted_alpha=0.1,
                    line_width=2,
                )
                legend_it.append(
                    (
                        str(np.round(float(data_dict["time_since"][0]), 2)) + " days  ",
                        [c],
                    )
                )
        # Range
        spectrum.y_range = Range1d(
            max(min(min_spec) - 0.1 * min(min_spec), -1),
            min(0.1 * max(max_spec) + max(max_spec), 5),
        )

    #################################
    # ADS data ######################
    #################################
    # Check if the spectra master file exists yet.
    elif exists(
        "static/SourceData/"
        + str(event_id)
        + "/"
        + str(event_id)
        + "_Spectra_Master.txt"
    ):
        # Get the files that were downloaded from the ADS
        spectra_df = pd.read_csv(
            "static/SourceData/"
            + str(event_id)
            + "/"
            + str(event_id)
            + "_Spectra_Master.txt",
            sep="\t",
        )

        ####### References ##########
        # Get the list of unique references
        spectra_refs = spectra_df["reference"]

        spectra_source_indices_sub = []
        for ref in spectra_refs:
            if ref in needed_dict.keys():
                spectra_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

            else:
                # Add to needed dict
                needed_dict[ref] = {
                    "names": dict_refs3[ref]["names"],
                    "year": dict_refs3[ref]["year"],
                }

                # Save the spectra ref to use as a key in event html when accessing the reference
                spec_refs.append(ref)

                spectra_source_indices_sub.append(
                    (list(needed_dict.keys()).index(ref) + 1)
                )

        # Add the lists of indices to the df
        spectra_df["indices"] = spectra_source_indices_sub

        # List all the epochs at which spectra were taken
        epochs = list(set(list(spectra_df["time"].astype(float))))
        epochs.sort()

        # Choose colours
        colour = viridis(len(epochs))

        # Plot
        for i in range(len(epochs)):

            # Scale the flux using the 5000A flux
            scaled_spectrum = spectra_df.loc[spectra_df["time"] == float(epochs[i])]
            if np.array(scaled_spectrum["flux"])[-1] < 5000:
                scaled_spectrum["scaled_flux"] = (
                    np.array(scaled_spectrum["flux"])
                    / np.array(scaled_spectrum["flux"])[0]
                )
            elif np.array(scaled_spectrum["flux"])[0] > 5000:
                scaled_spectrum["scaled_flux"] = (
                    np.array(scaled_spectrum["flux"])
                    / np.array(scaled_spectrum["flux"])[-1]
                )
            else:
                scaled_spectrum["scaled_flux"] = scaled_spectrum["flux"] / (
                    interp1d(
                        scaled_spectrum["rest_wavelength"], scaled_spectrum["flux"]
                    )
                )(np.array([5000]))
            # Perform scaling of the spectrum

            # Create a CDS
            spectra_cds = ColumnDataSource(scaled_spectrum)

            tooltips = [
                ("Rest wavelength", "@rest_wavelength{0}"),
                ("Obs. wavelength", "@obs_wavelength{0}"),
                ("Flux", "@scaled_flux"),
                ("Unit", "@flux_unit"),
                ("Instrument", "@instrument"),
                ("Time [days]", "@time"),
                ("Source", "@indices"),
            ]

            c = spectrum.line(
                "rest_wavelength",
                "scaled_flux",
                source=spectra_cds,
                color=colour[i],
                muted_color="gray",
                muted_alpha=0.1,
                line_width=2,
            )
            legend_it.append((str(np.round(float(epochs[i]), 2)) + " days  ", [c]))
    else:
        # Notify when there is no data present

        # Set a range so we can always centre the nodata for the spectra plot
        spectrum.x_range = Range1d(5000, 8000)
        spectrum.y_range = Range1d(0, 1)

        citation = Label(
            x=6100,
            y=0.405,
            x_units="data",
            y_units="data",
            text=processing_tag(event_id, "Optical Spectra"),
            render_mode="css",
            text_font_size="50pt",
            border_line_color="grey",
            border_line_alpha=0,
            text_alpha=0.2,
            background_fill_alpha=1.0,
            text_color="black",
        )
        spectrum.add_layout(citation)

    # Add the HoverTool to the figure
    spectrum.add_tools(HoverTool(tooltips=tooltips))

    # Aesthetics
    # Title
    spectrum.title.text_font_size = "20pt"
    spectrum.title.text_color = "black"
    spectrum.title.align = "center"

    # Axis font size
    spectrum.yaxis.axis_label_text_font_size = "16pt"
    spectrum.xaxis.axis_label_text_font_size = "16pt"

    # Font Color
    spectrum.xaxis.axis_label_text_color = "black"
    spectrum.xaxis.major_label_text_color = "black"

    spectrum.yaxis.axis_label_text_color = "black"
    spectrum.yaxis.major_label_text_color = "black"

    # Tick colors
    spectrum.xaxis.major_tick_line_color = "black"
    spectrum.yaxis.major_tick_line_color = "black"

    spectrum.xaxis.minor_tick_line_color = "black"
    spectrum.yaxis.minor_tick_line_color = "black"

    # Axis labels
    spectrum.xaxis.axis_label = "Rest Frame Wavelength [Å]"
    spectrum.yaxis.axis_label = "Flux"

    # Axis Colors
    spectrum.xaxis.axis_line_color = "black"
    spectrum.yaxis.axis_line_color = "black"

    # Make ticks larger
    spectrum.xaxis.major_label_text_font_size = "16pt"
    spectrum.yaxis.major_label_text_font_size = "16pt"

    spectrum.background_fill_color = "white"
    spectrum.border_fill_color = "white"

    # Sort the legends by time
    epochs = []
    for legend in legend_it:
        epochs.append(float(legend[0][:-7]))
    sort_index = np.argsort(epochs)
    legend_it = [legend_it[i] for i in sort_index]
    # Allow user to mute individual spectra by clicking the legend
    num = 35
    for i in range(math.ceil(len(legend_it) / num)):
        if i + 1 < len(legend_it) / num:
            legend2 = Legend(items=legend_it[i * num : i * num + num])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            spectrum.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"
        else:
            legend2 = Legend(items=legend_it[i * num : i * num + len(legend_it)])
            legend2.click_policy = "mute"
            legend2.orientation = "vertical"
            spectrum.add_layout(legend2, "left")
            legend2.label_text_font_size = "10pt"

    script, div = components(
        layout([radio], [optical], [xray], [spectrum], sizing_mode="scale_both")
    )
    kwargs = {"script": script, "div": div}
    kwargs["title"] = "bokeh-with-flask"

    # Return everything
    return render_template(
        "event.html",
        event=event,
        event_id=event_id,
        radec=radec,
        peakmag=peakmag,
        event_nos=event_nos,
        event_refs=event_refs,
        ptime_bandlist=ptime_bandlist,
        mag_bandlist=mag_bandlist,
        grb_time_str=grb_time_str,
        radec_nos=radec_nos,
        radec_refs=radec_refs,
        peakmag_refs=peakmag_refs,
        peakmag_nos=peakmag_nos,
        swift_refs=xray_refs,
        swift_nos=swift_reference_no,
        optical_refs=optical_refs,
        radio_refs=rad_refs,
        spec_refs=spec_refs,
        needed_dict=needed_dict,
        **kwargs,
    )


@app.route("/static/SourceData/<directory>", methods=["GET", "POST"])
def get_files2(directory):
    filestream = io.BytesIO()
    with zipfile.ZipFile(
        filestream, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zipf:
        for file in os.listdir(
            current_app.root_path + "/static/SourceData/" + directory
        ):
            zipf.write(
                current_app.root_path + "/static/SourceData/" + directory + "/" + file,
                directory + "/" + file,
            )
    filestream.seek(0)
    return send_file(filestream, download_name=directory + ".zip", as_attachment=True)


@app.route("/docs")
def docs():
    return render_template("docs.html")


# Download all of the database info from all tables as txt


@app.route("/master_table_download/")
def get_master_table():
    # Sql query to dataframe
    conn = get_db_connection()

    # Read the main db table
    df1 = pd.read_sql_query("SELECT * FROM SQLDataGRBSNe", conn)

    # The data from the Trig tables
    df2 = pd.read_sql("SELECT * FROM TrigCoords", conn)

    # Data for mags
    df3 = pd.read_sql("SELECT * FROM PeakTimesMags", conn)

    conn.close()

    # Write to an input output object
    # Main data
    s = io.StringIO()
    df1.to_csv(s, index=False)
    s.seek(0)

    # trigcoords
    t = io.StringIO()
    df2.to_csv(t, index=False)
    t.seek(0)

    # Peak mags
    u = io.StringIO()
    df3.to_csv(u, index=False)
    u.seek(0)

    downloads = [s, t, u]
    names = ["GRBSNdbdata.txt", "TrigsCoords.txt", "PeakMags.txt"]

    # Make the zipfile
    zipf = io.BytesIO()
    with zipfile.ZipFile(zipf, "w") as outfile:
        for i, file in enumerate(downloads):
            outfile.writestr(names[i], file.getvalue())

    zipf.seek(0)

    return send_file(
        zipf, mimetype="zip", download_name="GRBSNData.zip", as_attachment=True
    )


# The downloadable df data


@app.route("/table_download/<event_id>")
def get_table(event_id):
    # Sql query to dataframe
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM SQLDataGRBSNe", conn)
    df2 = pd.read_sql_query("SELECT * FROM TrigCoords", conn)
    df3 = pd.read_sql_query("SELECT * FROM PeakTimesMags", conn)
    conn.close()

    if "GRB" in event_id:
        # GRB202005A-SN2001a -  GRB is 0, 1, 2 so we want from 3 to the end of the split list
        # This solves the GRBs with SNs and without
        grb_name = str(event_id).split("-")[0][3:]

        # Set the index of the df to be based on GRB name
        downloadabledf = df.loc[df["GRB"] == grb_name]
        downloadabledf2 = df2.loc[df2["grb_id"] == grb_name]
        downloadabledf3 = df3.loc[df3["grb_id"] == grb_name]

    # This should ideally solve the lone SN cases
    else:
        sn_name = event_id[2:]

        # The list was empty because im searching for SN2020oi but the names in the database dont have the SN bit
        # Set the index of the df to be based on SN name
        downloadabledf = df.loc[df["SNe"] == sn_name]
        downloadabledf2 = df2.loc[df2["sn_name"] == sn_name]
        downloadabledf3 = df3.loc[df3["sn_name"] == sn_name]

    # Write to an input output object
    # Main data
    s = io.StringIO()
    downloadabledf.to_csv(s, index=False)
    s.seek(0)

    # trigcoords
    t = io.StringIO()
    downloadabledf2.to_csv(t, index=False)
    t.seek(0)

    # Peak mags
    u = io.StringIO()
    downloadabledf3.to_csv(u, index=False)
    u.seek(0)

    downloads = [s, t, u]
    names = ["GRBSNdbdata.txt", "TrigsCoords.txt", "PeakMags.txt"]

    # Make the zipfile
    zipf = io.BytesIO()
    with zipfile.ZipFile(zipf, "w") as outfile:
        for i, file in enumerate(downloads):
            outfile.writestr(names[i], file.getvalue())

    zipf.seek(0)

    return send_file(
        zipf, mimetype="zip", download_name=event_id + "_dbdata.zip", as_attachment=True
    )


# User modifiable graphs


@app.route("/graphing", methods=["GET", "POST"])  # Graphing tool
def graphs():
    category_dict = {
        "all": "all events",
        "orphan": "Orphan GRB Afterglows",
        "spec": "Spectroscopic SNe Only",
        "phot": "Photometric SNe Only",
    }
    name_dict = {
        "e_iso": "Eiso [erg]",
        "z": "Redshift",
        "ni_m": "SN Nickel Mass [M\u2609]",
        "ej_m": "SN Ejecta Mass [M\u2609]",
        "E_p": "GRB Peak Energy [erg]",
        "e_k": "SN Kinetic Energy [erg]",
        "T90": "T90 [sec]",
    }

    axis = {
        "e_iso": "log",
        "z": "linear",
        "ni_m": "linear",
        "ej_m": "linear",
        "E_p": "linear",
        "e_k": "log",
        "T90": "log",
    }
    if request.method == "POST":
        category = request.form.get("select1")
        x = request.form.get("select2")
        y = request.form.get("select3")

        conn = get_db_connection()  # Connect to DB

        if category == "all":
            # Get the data for the plots
            data = conn.execute(
                "SELECT DISTINCT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY GRB, SNe".format(
                    a=x, b=y
                )
            ).fetchall()

        elif category == "orphan":
            # Get the data for the plots
            data = conn.execute(
                "SELECT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE GRB IS NULL AND {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY SNe".format(
                    a=x, b=y
                )
            ).fetchall()

        elif category == "spec":
            # Get the data for the plots
            data = conn.execute(
                "SELECT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE SNe IS NOT NULL AND {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY SNe".format(
                    a=x, b=y
                )
            ).fetchall()

        elif category == "phot":
            # Get the data for the plots
            data = conn.execute(
                "SELECT GRB, SNe, Group_concat({a}, ','), Group_concat({b}, ',') FROM SQLDataGRBSNe WHERE SNe IS NULL  AND {a} IS NOT NULL AND {b} IS NOT NULL GROUP BY GRB".format(
                    a=x, b=y
                )
            ).fetchall()

        # Data for the graphs, remove the duplicates
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

        # Loop rows returned from SQL
        for row in data:
            grb_name.append(row[0])
            sne_name.append(row[1])
            #
            raw_x.append(str(row[2]).split(",")[0])
            raw_y.append(str(row[3]).split(",")[0])
            # Remove the first item from the returned list for plotting
            if (
                str(row[2]).split(",")[0] != "None"
                and str(row[3]).split(",")[0] != "None"
            ):

                if "<" in str(row[2]).split(",")[0]:
                    x_data_upperx.append(float(str(row[2]).split(",")[0][1:]))
                    y_data_upperx.append(float(str(row[3]).split(",")[0][1:]))
                elif ">" in str(row[2]).split(",")[0]:
                    x_data_lowerx.append(float(str(row[2]).split(",")[0][1:]))
                    y_data_lowerx.append(float(str(row[3]).split(",")[0][1:]))
                elif "<" in str(row[3]).split(",")[0]:
                    x_data_upperx.append(float(str(row[2]).split(",")[0][1:]))
                    y_data_upperx.append(float(str(row[3]).split(",")[0][1:]))
                elif ">" in str(row[3]).split(",")[0]:
                    x_data_lowerx.append(float(str(row[2]).split(",")[0][1:]))
                    y_data_lowerx.append(float(str(row[3]).split(",")[0][1:]))
                else:
                    x_data.append(float(str(row[2]).split(",")[0]))
                    y_data.append(float(str(row[3]).split(",")[0]))

        # Place the plotting data in a dict (the ones that arent uppper/lower limits)
        data_dict = {x: x_data, y: y_data}

        # Convert the dict to a column data object
        data_source = ColumnDataSource(data_dict)

        # Plot the data
        graph = figure(
            x_axis_type=str(axis[x]),
            y_axis_type=str(axis[y]),
            toolbar_location="right",
            plot_width=1200,
            plot_height=700,
        )
        graph.xaxis.ticker.desired_num_ticks = 2
        graph.yaxis.ticker.desired_num_ticks = 2
        graph.circle(x, y, source=data_source, size=10, fill_color="orange")
        graph.inverted_triangle(
            x_data_upperx, x_data_uppery, size=10, fill_color="blue"
        )
        graph.triangle(x_data_lowerx, x_data_lowery, size=10, fill_color="red")

        graph.inverted_triangle(y_data_upperx, y_data_uppery, size=10, fill_color="red")
        graph.triangle(y_data_lowerx, y_data_lowery, size=10, fill_color="red")

        # Aesthetics
        # Title
        graph.title.text_font_size = "13pt"
        graph.title.text_color = "black"
        graph.title.align = "center"

        # Axis labels
        graph.xaxis.axis_label = name_dict[x]
        graph.yaxis.axis_label = name_dict[y]

        graph.xaxis.axis_label_text_font_size = "13pt"
        graph.yaxis.axis_label_text_font_size = "13pt"

        # Axis Colors
        graph.xaxis.axis_line_color = "black"
        graph.yaxis.axis_line_color = "black"

        # Make ticks larger
        graph.xaxis.major_label_text_font_size = "13pt"
        graph.yaxis.major_label_text_font_size = "13pt"

        script, div = components(graph)
        kwargs = {"script": script, "div": div}
        kwargs["title"] = "bokeh-with-flask"

        return render_template(
            "graphs.html",
            grb_name=grb_name,
            sne_name=sne_name,
            raw_x=raw_x,
            raw_y=raw_y,
            txt_title=str(name_dict[y] + "vs" + name_dict[x]),
            **kwargs,
        )

    else:
        graph = figure(
            plot_width=400, plot_height=400, title=None, toolbar_location="right"
        )

        script, div = components(graph)
        kwargs = {"script": script, "div": div}
        kwargs["title"] = "bokeh-with-flask"
        return render_template("graphs.html", **kwargs)


# Allow download of the graphing page graph


@app.route("/graph_data/<title>/<grb_name>/<sne_name>/<raw_x>/<raw_y>")
def download_graph_data(title, grb_name, sne_name, raw_x, raw_y):
    # Zip the data for the downloadable files
    download = np.column_stack((grb_name, sne_name, raw_x, raw_y))
    s = io.StringIO()
    dwnld = np.savetxt(s, download, delimiter=" ", fmt="%s")
    s.seek(0)
    # Make the response
    resp = Response(s, mimetype="text/csv")

    name = str(title) + "grbsntool.txt"
    name = name.encode("utf-8")
    resp.headers.set("Content-Disposition", "attachment", filename=name)
    return resp


# Pass the data to be used by the dropdown menu (decorating)

# Help


@app.route("/help")
def get_help():
    return render_template("helppage.html")


# Allow search based on what people want to select from the catalogue


@app.route("/advsearch", methods=["POST", "GET"])
def advsearch():
    # Initially display this table selection
    conn = get_db_connection()
    initial_query = f"SELECT GRB, SNe, GROUP_CONCAT(e_iso), GROUP_CONCAT(z), GROUP_CONCAT(T90), GROUP_CONCAT(ej_m), GROUP_CONCAT(ni_m), GROUP_CONCAT(E_p), GROUP_CONCAT(e_k) FROM SQLDataGRBSNe GROUP BY GRB, SNe ORDER BY GRB, SNe;"
    data = conn.execute(initial_query).fetchall()
    conn.close()

    # The names of the events returned, used in another function to return the right files
    event_list = []
    for i in data:
        if i[0] != None:
            if i[1] != None and str(i[1][:4]).isnumeric():
                # Add the SN and GRB name
                event_list.append("GRB" + str(i[0]) + "-SN" + str(i[1]))
            elif i[1] != None and str(i[1][:4]).isnumeric() is False:
                # Add the SN and GRB name
                event_list.append("GRB" + str(i[0]) + "-" + str(i[1]))
            else:
                # GRB only
                event_list.append("GRB" + str(i[0]))
        elif i[1] != None:
            if str(i[1][:4]).isnumeric():
                # SN only
                event_list.append("SN" + str(i[1]))
            else:
                # SN only
                event_list.append(str(i[1]))

    # Create a form to take in user data
    form = TableForm(request.form)

    if request.method == "POST" and form.validate_on_submit():
        # List of vars to include in the query
        querylist = []
        varlist = []

        # Collect the variables
        event_id = form.object_name.data
        max_z = form.max_z.data
        min_z = form.min_z.data
        max_t90 = form.max_t90.data
        min_t90 = form.min_t90.data
        max_eiso = form.max_eiso.data
        min_eiso = form.min_eiso.data
        max_nim = form.max_nim.data
        min_nim = form.min_nim.data
        max_ejm = form.max_ejm.data
        min_ejm = form.min_ejm.data
        max_epeak = form.max_epeak.data
        min_epeak = form.min_epeak.data
        max_ek = form.max_ek.data
        min_ek = form.min_ek.data

        # Did they actually fill in the form
        k = 0
        for i in list(form.data.values())[:-2]:
            if i == "":
                k += 1
        if k == len(list(form.data.values())[:-2]):
            flash("You didn't enter any data")
            return redirect(url_for("advsearch"))

        # Check if the variables are as expected
        if event_id != str():

            if str(event_id)[2:] in sne:  # if they search an SNYYYYxx sn type
                querylist.append(f"SNe=?")
                varlist.append(str(event_id[2:]))

            elif str(event_id) in sne:  # if they search an non-SNYYYYxx sn type
                querylist.append(f"SNe=?")
                varlist.append(str(event_id))

            elif str(event_id)[3:] in grbs:  # if they search an GRB
                querylist.append(f"GRB=?")
                varlist.append(str(event_id[3:]))

            else:
                flash("This object is not in our database.")
                return redirect(url_for("advsearch"))

        # Redshift
        if min_z != str():
            # Error checking
            try:
                float(min_z)
            except ValueError:
                flash("Enter a float for the minimum redshift")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(z as FLOAT)>=?")
            varlist.append(float(min_z))

        if max_z != str():
            # Error checking
            try:
                float(max_z)
            except ValueError:
                flash("Enter a float for the maximum redshift")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(z as FLOAT)<=?")
            varlist.append(float(max_z))

        # T90
        if min_t90 != str():
            # Error checking
            try:
                float(min_t90)
            except ValueError:
                flash("Enter a float for the minimum T$_{90}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(T90 as FLOAT)>=?")
            varlist.append(float(min_t90))

        if max_t90 != str():
            # Error checking
            try:
                float(max_t90)
            except ValueError:
                flash("Enter a float for the maximum T$_{90}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(T90 as FLOAT)<=?")
            varlist.append(float(max_t90))

        # Eiso
        if min_eiso != str():
            # Error checking
            try:
                float(min_eiso)
            except ValueError:
                flash("Enter a float for the minimum E$_{iso}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(e_iso as FLOAT)>=?")
            varlist.append(float(min_eiso))

        if max_eiso != str():
            # Error checking
            try:
                float(max_eiso)
            except ValueError:
                flash("Enter a float for the maximum E$_{iso}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(e_iso as FLOAT)<=?")
            varlist.append(float(max_eiso))

        # Epeak
        if min_epeak != str():
            # Error checking
            try:
                float(min_epeak)
            except ValueError:
                flash("Enter a float for the minimum E$_{p}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(E_p as FLOAT)>=?")
            varlist.append(float(min_epeak))

        if max_epeak != str():
            # Error checking
            try:
                float(max_epeak)
            except ValueError:
                flash("Enter a float for the maximum E$_{p}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(E_p as FLOAT)<=?")
            varlist.append(float(max_epeak))

        # Ek
        if min_ek != str():
            # Error checking
            try:
                float(min_ek)
            except ValueError:
                flash("Enter a float for the minimum E$_{k}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(e_k as FLOAT)>=?")
            varlist.append(float(min_ek))

        if max_ek != str():
            # Error checking
            try:
                float(max_ek)
            except ValueError:
                flash("Enter a float for the maximum E$_{k}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(e_k as FLOAT)<=?")
            varlist.append(float(max_ek))

        # Nickel Mass
        if min_nim != str():
            # Error checking
            try:
                float(min_nim)
            except ValueError:
                flash("Enter a float for the minimum M$_{Ni}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(ni_m as FLOAT)>=?")
            varlist.append(float(min_nim))

        if max_nim != str():
            # Error checking
            try:
                float(max_nim)
            except ValueError:
                flash("Enter a float for the maximum M$_{Ni}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(ni_m as FLOAT)<=?")
            varlist.append(float(max_nim))

        # Ejecta Mass
        if min_ejm != str():
            # Error checking
            try:
                float(min_ejm)
            except ValueError:
                flash("Enter a float for the minimum M$_{Ej}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(ej_m as FLOAT)>=?")
            varlist.append(float(min_ejm))

        if max_ejm != str():
            # Error checking
            try:
                float(max_ejm)
            except ValueError:
                flash("Enter a float for the maximum M$_{Ej}$")
                return redirect(url_for("advsearch"))
            # Appending
            querylist.append(f"CAST(ej_m as FLOAT)<=?")
            varlist.append(float(max_ejm))

        # Build the query using the user filters
        query = str()

        start_query = f"SELECT GRB, SNe, GROUP_CONCAT(e_iso), GROUP_CONCAT(z), GROUP_CONCAT(T90), GROUP_CONCAT(ej_m), GROUP_CONCAT(ni_m), GROUP_CONCAT(E_p), GROUP_CONCAT(e_k) FROM SQLDataGRBSNe"

        query += start_query

        mid_query = str()
        for i in range(len(varlist)):
            if i == 0:
                mid_query += " WHERE " + querylist[i]

            elif i == len(varlist) - 1:
                mid_query += " AND " + querylist[i] + " "

            else:
                mid_query += " AND " + querylist[i]

        end_query = f"GROUP BY GRB, SNe ORDER BY GRB, SNe;"
        query += mid_query + end_query

        # Connect to the db and make query
        conn = get_db_connection()
        data = conn.execute(query, (varlist)).fetchall()
        conn.close()

        # The names of the events returned, used in another function to return the right files
        event_list = []
        for i in data:
            if i[0] != None:
                if i[1] != None and str(i[1][:4]).isnumeric():
                    # Add the SN and GRB name
                    event_list.append("GRB" + str(i[0]) + "-SN" + str(i[1]))
                elif i[1] != None and str(i[1][:4]).isnumeric() is False:
                    # Add the SN and GRB name
                    event_list.append("GRB" + str(i[0]) + "-" + str(i[1]))
                else:
                    # GRB only
                    event_list.append("GRB" + str(i[0]))
            elif i[1] != None:
                if str(i[1][:4]).isnumeric():
                    # SN only
                    event_list.append("SN" + str(i[1]))
                else:
                    # SN only
                    event_list.append(str(i[1]))

        return render_template(
            "advancedsearch.html",
            form=form,
            data=data,
            mid_query=mid_query,
            varlist=varlist,
            event_list=event_list,
        )

    return render_template(
        "advancedsearch.html",
        form=form,
        data=data,
        mid_query="",
        varlist="",
        event_list=event_list,
    )


# Function to download the user generated table


@app.route("/get_advsearch_table", defaults={"query": "", "varlist": ""})
@app.route("/<query>/<varlist>/get_advsearch_table", methods=["GET", "POST"])
def get_advsearch_table(query, varlist):

    if varlist != "":
        # Convert the string to a list
        varlist = ast.literal_eval(varlist)

    # Sql query to dataframe
    conn = get_db_connection()
    if query == "":
        # Read the main db table
        df1 = pd.read_sql_query("SELECT * FROM SQLDataGRBSNe", conn)

        # The data from the Trig tables
        df2 = pd.read_sql("SELECT * FROM TrigCoords", conn)

        # Data for mags
        df3 = pd.read_sql("SELECT * FROM PeakTimesMags", conn)
    else:
        # Read the main db table
        df1 = pd.read_sql_query(
            "SELECT * FROM SQLDataGRBSNe" + query,
            conn,
            params=tuple(
                varlist,
            ),
        )

        # The data from the Trig tables
        df2 = pd.read_sql("SELECT * FROM TrigCoords", conn)

        # Data for mags
        df3 = pd.read_sql("SELECT * FROM PeakTimesMags", conn)

    conn.close()

    # Write to an input output object
    # Main data
    s = io.StringIO()
    df1.to_csv(s, index=False)
    s.seek(0)

    # trigcoords
    t = io.StringIO()
    df2.to_csv(t, index=False)
    t.seek(0)

    # Peak mags
    u = io.StringIO()
    df3.to_csv(u, index=False)
    u.seek(0)

    downloads = [s, t, u]
    names = ["GRBSNdbdata.txt", "TrigsCoords.txt", "PeakMags.txt"]

    # Make the zipfile
    zipf = io.BytesIO()
    with zipfile.ZipFile(zipf, "w") as outfile:
        for i, file in enumerate(downloads):
            outfile.writestr(names[i], file.getvalue())

    zipf.seek(0)

    return send_file(
        zipf, mimetype="zip", download_name="GRBSNData.zip", as_attachment=True
    )


@app.route("/megadownload/<directory_list>", methods=["GET", "POST"])
def get_observations(directory_list):

    # Convert the string to a list
    directory_list = ast.literal_eval(directory_list)

    filestream = io.BytesIO()
    with zipfile.ZipFile(
        filestream, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as zipf:
        for folder in directory_list:
            for file in os.listdir(
                current_app.root_path + "/static/SourceData/" + folder + "/"
            ):
                zipf.write(
                    current_app.root_path + "/static/SourceData/" + folder + "/" + file,
                    folder + "/" + file,
                )
    filestream.seek(0)
    return send_file(filestream, download_name="Observations.zip", as_attachment=True)


# Run app
if __name__ == "__main__":
    # debug=True lets you do it without rerunning all the time

    app.run(debug=True)
