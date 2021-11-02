import pandas as pd
import numpy as np

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

#Photometry
names = sne_names()
ras = []
decs = []

print(names)
for i in range(len(names)):

	#Account for AT transients

	if names[i][0]!= 'A':
		print(names[i])

		#Use the API to get the magnitude, times and their errors, in all bands, as a csv
		data = pd.read_csv('https://api.astrocats.space/SN'+str(names[i])+'/photometry/time+magnitude+e_magnitude+band+ra+dec?format=csv')

		#File to save the csv 
		#save the data
		data.to_csv('./SNE-OpenSN-Data/photometry/'+str(names[i])+'.csv', index=False)


		#RA and Dec 
		ra = [pd.read_json('https://api.astrocats.space/SN'+str(names[i])+'/ra?first&format=json')]
		dec = [pd.read_json('https://api.astrocats.space/SN'+str(names[i])+'/dec?first')]
		

		ras.append(ra['SN'+str(names[i])]['ra']['value'])
		decs.append(dec['SN'+str(names[i])]['dec']['value'])

	elif names[i][0]== '2021djjd' or 'NULL':
		continue 
	else:
		print('Non numeric', names[i])

		#Use the API to get the magnitude, times and their errors, in all bands, as a csv
		data = pd.read_csv('https://api.astrocats.space/'+str(names[i])+'/photometry/time+magnitude+e_magnitude+band+ra+dec?format=csv')

		#File to save the csv 
		#save the data
		data.to_csv('./SNE-OpenSN-Data/photometry/'+str(names[i])+'.csv', index=False)


		#RA and Dec 
		ra = [pd.read_json('https://api.astrocats.space/'+str(names[i])+'/ra?first')]
		dec = [pd.read_json('https://api.astrocats.space/'+str(names[i])+'/dec?first')]		

		ras.append(ra[str(names[i])]['ra']['value'])
		decs.append(dec[str(names[i])]['dec']['value'])


	