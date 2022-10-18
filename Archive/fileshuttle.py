'''
This was designed to shuttle the xrtlc files for a GRB-SN to the SourceData file for thatGRBSN, but it isn't needed anymore. 
'''

import numpy as np
import os
from csv import writer
import shutil

#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect('./Webtool/static/Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

def grb_names():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT(GRB) FROM SQLDataGRBSNe')
    grb = []
    for i in names:
    	
    	if i[0] == None:
    		continue

    	#Select only the correct names
    	else:
    		grb.append(i[0])
    conn.close()
    
    return grb

def pairs():
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT GRB, SNe FROM SQLDataGRBSNe WHERE GRB IS NOT NULL')

    grb = grb_names()
    name_dict = {}


    for i in names:
    	if str(i[1])=='None':
    		name_dict[i[0]] = 'GRB'+i[0]

    	elif 'AT' in str(i[1]):
    		name_dict[i[0]] = 'GRB'+i[0]+'-'+i[1]

    	else:
    		name_dict[i[0]] = 'GRB'+i[0]+'-SN'+i[1]

        
    conn.close()
    
    
    return name_dict

#Loop the names and go to the api and download the data
#It will be saved to ./SNE-OpenSN-Data/photometry or spectra depending

#Photometry+Spectra
names = grb_names()
print(names)
pairs = pairs()

#Find out if Antonios tool picked up a file for each pair.
root = os.getcwd()

long_grbs = []
for x in os.listdir(root+'/Webtool/static/long_grbs'):
    if x.endswith(".txt"):
        # Prints only text file present in My Folder
        long_grbs.append(str(x))


file_source = '/Webtool/static/long_grbs/'
file_destination = '/Webtool/static/SourceData/'

for i in long_grbs:
    print(str(i).replace('xrtlc.txt', '')[3:])
    if str(i).replace('xrtlc.txt', '')[3:] in names:

		#Add a line to the csv which contains details of where these came from 
        swift = [str(pairs[str(i).replace('xrtlc.txt', '')[3:]]), str(i), 'Xray', 'https://www.swift.ac.uk/xrt_curves/']
        with open('./Webtool/static/SourceData/'+pairs[str(i).replace('xrtlc.txt', '')[3:]]+'/'+str(pairs[str(i).replace('xrtlc.txt', '')[3:]])+'filesources.csv', 'a', newline='') as file:
            writer_obj = writer(file)
            writer_obj.writerow(swift)
            file.close()

for i in long_grbs:
	if str(i).replace('xrtlc.txt', '')[3:] in names:

		shutil.move(os.path.join(root+file_source, i), os.path.join(root+file_destination+pairs[str(i).replace('xrtlc.txt', '')[3:]], i))


