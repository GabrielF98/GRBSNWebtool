'''
Takes the file name and source data for each GRB-SN
from a notion export and creates/updates the
filesources.csv file for that GRB-SN.
Also includes the references for the swift data and the OpenSN data.
'''

import argparse
import glob
import os
from csv import writer
from os.path import exists

import pandas as pd

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--grbsn', type=str, required=False)
    args = parser.parse_args()

    root = os.getcwd()

    if args.grbsn:
        file_list = [args.grbsn]

    else:
        dirs = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

        file_list = []
        for i in dirs:
            if 'GRB' in str(i) or 'SN' in str(i):
                file_list.append(i)

    # Go into the notion export and find the source list for the GRB or SN
    loc = '/NotionExport/'
    root = root+loc
    dirs2 = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

    for i in dirs2:
        if 'Download' in str(i):
            sourcefolder1 = str(i)+'/'

    root = root+sourcefolder1
    dirs3 = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

    for i in dirs3:
        if 'Source List' in str(i):
            sourcefolder2 = str(i)+'/'

    root = root+sourcefolder2
    dirs4 = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

    # loop over the GRB-SN name list
    for j in file_list:
        for i in dirs4:
            if str(j) in str(i):
                #List the csvs in this folder (i)
                csv_files = glob.glob(os.path.join(root+i, "*.csv"))

                #Read in the first csv (for some reason there are doubles of everything)
                df = pd.read_csv(csv_files[0])

                #Add a column saying what GRB-SN this is
                length = len(df)
                name_col = [j]*length

                df.insert(0, 'GRB/SN', name_col)

                #Write to a csv for these GRBs
                df.to_csv('./'+str(j)+'/'+str(j)+'filesources.csv', sep=',', index=False)

    ## Add the bit for XRT LC references
    for i in file_list:
        # Make sure a filesources.csv file exists for all off the GRB-SNe
        if exists('./'+i+'/'+i+'filesources.csv'):
            # Find out if we have already added Swift if the file exists. Set k=1
            xtrname = pd.read_csv('./'+i+'/'+i+'filesources.csv', header=0)
            filenames = list(xtrname['Filename'].astype(str))
            k=0
            for name in filenames:
                if 'xrtlc' in str(name):
                    k=1

        # If it doesn't exist make one and set k=0
        else:
            k == 0
            with open('./'+i+'/'+i+'filesources.csv', 'w', newline='', encoding='utf-8') as file:
                writer_obj = writer(file)
                writer_obj.writerow(['GRB/SN', 'Filename', 'Datatypes', 'Reference'])

        # XRT stuffs
        files = os.listdir(i)
        for j in files:
            #print(j)
            if str('xrtlc') in str(j) and k==0:
                #Write to the csv of sources
                with open('./'+i+'/'+i+'filesources.csv', 'a', newline='', encoding='utf-8') as file:
                    writer_obj = writer(file)

                    writer_obj.writerow([str(i), str(i).split('-', maxsplit=1)[0]+'xrtlc.txt',
                        'Xray', 'https://www.swift.ac.uk/xrt_curves/'])

    ## Add the bit for OpenSN data
    for i in file_list:
        print("i is:", i)
        if 'SN' in str(i)[:2]:
            name = list(str(i).split('-'))[0]
        elif len(str(i))>11:
            name = list(str(i).split('-'))[1]

        files = os.listdir(i)
        for j in files:
            #print(j)
            if str('OpenSNPhotometry') in str(j):
                print(str(i))
                #Write to the csv of sources
                with open('./'+i+'/'+i+'filesources.csv', 'a', newline='', encoding='utf-8') as file:
                    writer_obj = writer(file)
                    writer_obj.writerow([i, j, 'Optical',
                        'https://api.astrocats.space/'+name+'/photometry/time+magnitude+e_magnitude+band+ra+dec+source?format=csv'])

        for j in files:
            if str('OpenSNSpectra') in str(j):
                #Write to the csv of sources
                with open('./'+i+'/'+i+'filesources.csv', 'a', newline='', encoding='utf-8') as file:
                    writer_obj = writer(file)

                    writer_obj.writerow([i, j, 'Spectra',
                        'https://api.astrocats.space/'+name+'/spectra/?item='+str(str(j).replace("OpenSNSpectra", "")).replace('.json', "")+'&format=json'])
