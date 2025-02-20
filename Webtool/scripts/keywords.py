'''
This is going to be a file that I can run to tell me all the tags that have been used in the master files for the webtool.
'''

import os

import pandas as pd

# List of GRB-SNe that I have text file data on so far.
PATH_TO_SOURCE_DATA = "../static/SourceData/"
dirs = [
    item
    for item in os.listdir(PATH_TO_SOURCE_DATA)
    if os.path.isdir(os.path.join(PATH_TO_SOURCE_DATA, item))
]

trial_list = []
for i in dirs:
    if 'GRB' in str(i) or 'SN' in str(i):
        trial_list.append(i)

# Go through the list of folders and check for master files. If there are any then add the tags from those files to the master lists for radio, optical and xray.
xray_keywords = []
radio_keywords = []
optical_keywords = []
spectra_keywords = []

# date formats used
date_formats = []

# Loop over the Master files.
for i in range(len(trial_list)):
    print(trial_list[i])
    if os.path.exists(
        os.path.join(
            PATH_TO_SOURCE_DATA,
            trial_list[i],
            trial_list[i] + "_Optical_Master.txt",
        )
    ):
        op_master = pd.read_csv(
            os.path.join(
                PATH_TO_SOURCE_DATA,
                trial_list[i],
                trial_list[i] + "_Optical_Master.txt",
            ),
            header=0,
            sep="\t",
            index_col=None,
        )
        optical_keywords = optical_keywords + list(op_master.keys())

        if "date_unit" in list(op_master.keys()):
            date_formats = date_formats + list(op_master["date_unit"])

    if os.path.exists(
        os.path.join(
            PATH_TO_SOURCE_DATA,
            trial_list[i],
            trial_list[i] + "_Radio_Master.txt",
        )
    ):
        rad_master = pd.read_csv(
            os.path.join(
                PATH_TO_SOURCE_DATA,
                trial_list[i],
                trial_list[i] + "_Radio_Master.txt",
            ),
            header=0,
            sep="\t",
            index_col=None,
        )
        radio_keywords = radio_keywords + list(rad_master.keys())

        if "date_unit" in list(rad_master.keys()):
            date_formats = date_formats + list(rad_master["date_unit"])

    if os.path.exists(
        os.path.join(
            PATH_TO_SOURCE_DATA,
            trial_list[i],
            trial_list[i] + "_Spectra_Master.txt",
        )
    ):
        spec_master = pd.read_csv(
            os.path.join(
                PATH_TO_SOURCE_DATA,
                trial_list[i],
                trial_list[i] + "_Spectra_Master.txt",
            ),
            header=0,
            sep="\t",
            index_col=None,
        )
        spectra_keywords = spectra_keywords + list(spec_master.keys())

    if os.path.exists(
        os.path.join(
            PATH_TO_SOURCE_DATA,
            trial_list[i],
            trial_list[i] + "_Xray_Master.txt",
        )
    ):
        x_master = pd.read_csv(
            os.path.join(
                PATH_TO_SOURCE_DATA,
                trial_list[i],
                trial_list[i] + "_Xray_Master.txt",
            ),
            header=0,
            sep="\t",
            index_col=None,
        )
        xray_keywords = xray_keywords + list(x_master.keys())

        if "date_unit" in list(x_master.keys()):
            date_formats = date_formats + list(x_master["date_unit"])


xray = list(set(xray_keywords))
radio = list(set(radio_keywords))
optical = list(set(optical_keywords))
spectra = list(set(spectra_keywords))

dateunits = list(set(date_formats))

# Prints
print('The xray master files use these keywords: \n')
print(xray)
print(len(xray))
print('The optical master files use these keywords: \n')
print(optical)
print(len(optical))
print('The radio master files use these keywords: \n')
print(radio)
print(len(radio))
print('The spectra master files use these keywords: \n')
print(spectra)
print(len(spectra))

print('These units are used for dates: \n')
print(dateunits)
print(len(dateunits))
