'''
Create a new folder, OriginalFormats, filesources.csv and readme.txt file for a GRB-SN.
'''

import argparse
import json
import os

import numpy as np
import pandas as pd
import requests

from yaml2db import _load_yaml_config, dict2db


def readDatabase(databaseID, headers):
    # Find new GRB-SNe in Notion
    # Initialisation
    token = 'secret_NQONcPqFCcw0jzEHQ2gxcPyhzrIy0lizo5LLp0eWRvF'
    databaseID = "c1f1bfea218c40e2a1267b9e69618838"
    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Notion-Version": "2022-02-22"
    }
    readUrl = f"https://api.notion.com/v1/databases/{databaseID}/query"
    res = requests.request("POST", readUrl, headers=headers)
    data = res.json()
    print(res.status_code)
    # print(res.text)
    bundle = data['results']
    event_names = []
    for page_list in bundle:
        for page in page_list:
            properties = page_list['properties']
            name = properties['Name']
            name = name['title'][0]['text']['content']
            event_names.append(name)

    # with open('./full-properties.json', 'w', encoding='utf8') as f:
    #     json.dump(data, f, ensure_ascii=False)
    # return data

    return list(set(event_names))


def create_new_stuff(event_list):
    # List all GRB-SN folders in source data.
    folders = []
    rootdir = 'Webtool/static/SourceData'
    for it in os.scandir(rootdir):
        if it.is_dir():
            folders.append(it.path.split('/')[-1])

    # Check if any GRB-SN have not yet been created.
    for event in event_list:
        if event not in folders:
            # print(f'{event} is missing.')

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
                yaml_db_info['PeakTimesMags']['sn_name'] = event.split(
                    '-')[1][2:]
                yaml_db_info['PeakTimesMags']['grb_id'] = event.split(
                    '-')[0][3:]
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


def main(event_name):
    if event_name:
        create_new_stuff(event_list=[event_name])

    else:
        notion_events = readDatabase(databaseID, headers)
        create_new_stuff(notion_events)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Pass the new GRB-SN name to the script')
    parser.add_argument('--file', type=str, required=False)
    args = parser.parse_args()
    main(args.file)
