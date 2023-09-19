'''
Create a new folder, OriginalFormats, filesources.csv and readme.txt file for a GRB-SN.
Create a Notion entry for a new GRB-SN.
'''

import os

import numpy as np
import pandas as pd

# Find new GRB-SNe
notion_events = pd.read_csv('Webtool/static/SourceData/tags.csv')

# List all GRB-SN folders in source data.
folders = []
rootdir = 'Webtool/static/SourceData'
for it in os.scandir(rootdir):
    if it.is_dir():
        folders.append(it.path.split('/')[-1])

print(folders)

# Check if any GRB-SN have not yet been created.
for event in notion_events['Name']:
    if event not in folders:
        print(f'{event} is missing.')

        # Create the folder
        os.chdir('Webtool/static/SourceData')
        os.mkdir(event)
        os.chdir(event)

        # Create the readme.txt

        # Create filesources.csv

        # Create Original formats folder.

        # Create a blank entry in the DB.
