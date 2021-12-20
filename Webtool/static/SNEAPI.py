import pandas as pd
import numpy as np
import json
import os
import shutil
import requests

#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

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


#Loop the names and go to the api and download the data
#It will be saved to ./SNE-OpenSN-Data/photometry or spectra depending

#Photometry+Spectra
names = sne_names()
  
# Directories for the spectra
for i in names:
	dir = './SNE-OpenSN-Data/spectraJSON/'+str(i)
	if os.path.exists(dir):
   		shutil.rmtree(dir)
	else:
		os.mkdir(dir)

#Loop over the filenames and request the data about these events
for i in range(len(names)):

	if names[i][0]!= 'A':
		print(names[i])

		#Use the API to get the magnitude, times and their errors, in all bands, as a csv
		data = pd.read_csv('https://api.astrocats.space/SN'+str(names[i])+'/photometry/time+magnitude+e_magnitude+band+ra+dec?format=csv')

		#File to save the csv 
		#save the data
		data.to_csv('./SNE-OpenSN-Data/photometry/'+str(names[i])+'.csv', index=False)
		
		#Spectra
		#Use the API to get the time and all spectra, as a csv
		n=0
		
		placeholder = []

		while n>=0:
			print(n)
			data =	requests.get('https://api.astrocats.space/SN'+str(names[i])+'/spectra/?item='+str(n)+'&format=json')
			data = data.json()

			if data['SN'+names[i]]['spectra'] == [] or data['SN'+names[i]]['spectra']==placeholder:
				print(-1)
				n=-1

			else:
				file = open('./SNE-OpenSN-Data/spectraJSON/'+str(names[i])+'/'+str(names[i])+'_'+str(n)+'.json', 'w')
				json.dump(data, file)

				n+=1

			placeholder = data['SN'+names[i]]['spectra']

	elif names[i][0]=='NULL':
		continue

	else:
		print(names[i])
		#Use the API to get the magnitude, times and their errors, in all bands, as a csv
		data = requests.get('https://api.astrocats.space/'+str(names[i])+'/photometry/time+magnitude+e_magnitude+band+ra+dec?format=csv')

		print(data.keys())
		#File to save the csv 
		#save the data
		data.to_csv('./SNE-OpenSN-Data/photometry/'+str(names[i])+'.csv', index=False)

		#Spectra
		#Use the API to get the time and all spectra, as a csv
		n=0
		placeholder = pd.DataFrame(columns=['Placeholder'])

		while n>=0:
			print(n)
			data = json.loads('https://api.astrocats.space/'+str(names[i])+'/spectra/data?item='+str(n)+'&format=json')
			
			if "message" in data.keys()[0] or data.equals(placeholder):
				n=-1

			else:
				json.dump(data, './SNE-OpenSN-Data/spectraJSON/'+str(names[i])+'/'+str(names[i])+'_'+str(n)+'.json')

				n+=1

			placeholder = data