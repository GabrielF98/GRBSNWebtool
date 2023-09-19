'''
Create a new folder, OriginalFormats, filesources.csv and readme.txt file for a GRB-SN.
'''

import os

import numpy as np
import pandas as pd

from yaml2db import _load_yaml_config, dict2db

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
        cwd = os.getcwd()
        os.chdir('Webtool/static/SourceData')
        os.mkdir(event)
        os.chdir(event)

        # Create the readme.txt
        with open('readme.txt', 'w') as file:
            file.write(f'Event Name: {event}\n')
            file.write(
                '=========================================================\n')
            file.write('Filename:\n')
            file.write(
                '---------------------------------------------------------\n')

        # Create filesources.csv
        with open(event+'filesources.csv', 'w') as file:
            file.write('GRB/SN, Filename, Status, Reference\n')

        # Create Original formats folder.
        os.mkdir('OriginalFormats')

        # Change back to the right directory
        os.chdir(cwd)

        # Create a blank entry in the DBs.
        yaml_db_info = _load_yaml_config('database_entry.yaml')
        if len(event.split('-')) == 2:
            yaml_db_info['PeakTimesMags']['sn_name'] = event.split('-')[1][2:]
            yaml_db_info['PeakTimesMags']['grb_id'] = event.split('-')[0][3:]
            yaml_db_info['TrigCoords']['sn_name'] = event.split('-')[1][2:]
            yaml_db_info['TrigCoords']['grb_id'] = event.split('-')[0][3:]
            yaml_db_info['SQLDataGRBSNe']['GRB'] = event.split('-')[0][3:]
            yaml_db_info['SQLDataGRBSNe']['SNe'] = event.split('-')[1][2:]

        elif len(event.split('-')) == 1:
            if event[0] == 'S':
                yaml_db_info['PeakTimesMags']['sn_name'] = event[2:]
                yaml_db_info['TrigCoords']['sn_name'] = event[2:]
                yaml_db_info['SQLDataGRBSNe']['SNe'] = event[2:]

            elif event[0] == 'G':
                yaml_db_info['PeakTimesMags']['grb_id'] = event[3:]
                yaml_db_info['TrigCoords']['grb_id'] = event[3:]
                yaml_db_info['SQLDataGRBSNe']['GRB'] = event[3:]

        dict2db(yaml_db_info)
