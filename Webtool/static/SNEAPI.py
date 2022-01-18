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

# # Directories for the photometry
# for k in names:
# 	dir = './SNE-OpenSN-Data/photJSON/'+str(k)
# 	if os.path.exists(dir):
#    		shutil.rmtree(dir)
# 	else:
# 		os.mkdir(dir)
  
# # Directories for the spectra
# for j in names:
# 	dir = './SNE-OpenSN-Data/spectraJSON/'+str(j)
# 	if os.path.exists(dir):
#    		shutil.rmtree(dir)
# 	else:
# 		os.mkdir(dir)

#Loop over the filenames and request the data about these events
for i in range(len(names)):

	if names[i][0]!= 'A':
		print(names[i])

		#List of reference sources for this SN
		ref_list = requests.get('https://api.astrocats.space/'+str(names[i])+'/sources/?format=json')
		ref_list = ref_list.json()

		################################
		########PHOTOMETRY##############
		################################

		#Use the API to get the photometry in its entirety
		phot_source = requests.get('https://api.astrocats.space/SN'+str(names[i])+'/photometry/?format=json')
		phot_source = phot_source.json()
		
		#Convert the sources to have names
		if len(phot_source['SN'+names[i]]['photometry'])!=0:
			for m in phot_source['SN'+names[i]]['photometry']:

				list_of_sources = []

				for n in m['source'].split(','):
					keys = ref_list[str(names[i])]['sources'][int(n)-1].keys()

					if 'bibcode' in keys:
						string = ref_list[str(names[i])]['sources'][int(n)-1]['reference']
						string = string.replace("(","").replace(")","")
						print(string)
						ref = {'name':string, 
								'url':'https://ui.adsabs.harvard.edu/abs/'+str(ref_list[str(names[i])]['sources'][int(n)-1]['bibcode'])+'/abstract'} #ADS link from bibcode

						list_of_sources.append(ref)
					elif 'url' in keys:
						ref = {'name':ref_list[str(names[i])]['sources'][int(n)-1]['name'], 
								'url':ref_list[str(names[i])]['sources'][int(n)-1]['url']}
						list_of_sources.append(ref)

				print(list_of_sources)
				m['source'] = list_of_sources

		#Save the data
		file = open('./SNE-OpenSN-Data/photJSON/'+str(names[i])+'/'+str(names[i])+'.json', 'w')
		json.dump(phot_source, file)

		################################
		#######SPECTRA##################
		################################

		#Use the API to get the time and all spectra, as a csv
		n=0
		
		#The first result will act as a placeholder. 
		#When we have downloaded all the spectra it goes back to get the first data
		#This placeholder will be used to stop the loop at this point
		data = requests.get('https://api.astrocats.space/SN'+str(names[i])+'/spectra/?item='+str(n)+'&format=json')
		data = data.json()
		initial = len(data['SN'+names[i]]['spectra'])

		while n>=0:
			#print(n, len(data['SN'+names[i]]['spectra']))
			data = requests.get('https://api.astrocats.space/SN'+str(names[i])+'/spectra/?item='+str(n)+'&format=json')
			data = data.json()
			
			if len(data['SN'+names[i]]['spectra']) != initial or len(data['SN'+names[i]]['spectra'])==0:
				#print(-1)
				n=-1

			else:
				#Get references
				list_of_sources = []
				sources = data['SN'+names[i]]['spectra']['source'].split(',')

				for j in sources:
					keys = ref_list[str(names[i])]['sources'][int(j)-1].keys()

					if 'bibcode' in keys:
						string = ref_list[str(names[i])]['sources'][int(j)-1]['reference']
						string = string.replace("(","").replace(")","")
						print(string)
						ref = {'name':string, 
								'url':'https://ui.adsabs.harvard.edu/abs/'+str(ref_list[str(names[i])]['sources'][int(j)-1]['bibcode'])+'/abstract'} #ADS link from bibcode

						list_of_sources.append(ref)
					elif 'url' in keys:
						ref = {'name':ref_list[str(names[i])]['sources'][int(j)-1]['name'], 
								'url':ref_list[str(names[i])]['sources'][int(j)-1]['url']}
						list_of_sources.append(ref)
				data['SN'+names[i]]['spectra']['source'] = list_of_sources

				#Save the data
				file = open('./SNE-OpenSN-Data/spectraJSON/'+str(names[i])+'/'+str(names[i])+'_'+str(n)+'.json', 'w')
				json.dump(data, file)

				n+=1

	elif names[i][0]=='NULL':
		continue

	else: #AT2019
		print(names[i])

		#List of reference sources for this SN
		ref_list = requests.get('https://api.astrocats.space/'+str(names[i])+'/sources/?format=json')
		ref_list = ref_list.json()

		################################
		########PHOTOMETRY##############
		################################

		#Use the API to get the photometry in its entirety
		phot_source = requests.get('https://api.astrocats.space/'+str(names[i])+'/photometry/?format=json')
		phot_source = phot_source.json()
		
		print(phot_source)
		#Convert the sources to have names
		if len(phot_source[names[i]]['photometry'])!=0:
			for m in phot_source[names[i]]['photometry']:
				
				list_of_sources = []

				for n in m['source'].split(','):
					keys = ref_list[str(names[i])]['sources'][int(n)-1].keys()

					if 'bibcode' in keys:
						string = ref_list[str(names[i])]['sources'][int(n)-1]['reference']
						string = string.replace("(","").replace(")","")
						print(string)
						ref = {'name':string, 
								'url':'https://ui.adsabs.harvard.edu/abs/'+str(ref_list[str(names[i])]['sources'][int(n)-1]['bibcode'])+'/abstract'} #ADS link from bibcode

						list_of_sources.append(ref)
					elif 'url' in keys:
						ref = {'name':ref_list[str(names[i])]['sources'][int(n)-1]['name'], 
								'url':ref_list[str(names[i])]['sources'][int(n)-1]['url']}
						list_of_sources.append(ref)

				print(list_of_sources)
				m['source'] = list_of_sources

			#Save the data
			file = open('./SNE-OpenSN-Data/photJSON/'+str(names[i])+'/'+str(names[i])+'.json', 'w')
			json.dump(phot_source, file)


		################################
		#######SPECTRA##################
		################################

		#Use the API to get the time and all spectra, as a csv
		n=0
		
		#The first result will act as a placeholder. 
		#When we have downloaded all the spectra it goes back to get the first data
		#This placeholder will be used to stop the loop at this point
		data = requests.get('https://api.astrocats.space/'+str(names[i])+'/spectra/?item='+str(n)+'&format=json')
		data = data.json()
		initial = len(data[names[i]]['spectra'])

		while n>=0:
			data = requests.get('https://api.astrocats.space/'+str(names[i])+'/spectra/?item='+str(n)+'&format=json')
			data = data.json()
			
			if len(data[names[i]]['spectra']) != initial or len(data[names[i]]['spectra'])==0:
				n=-1

			else:
				#Get references
				list_of_sources = []
				sources = data[names[i]]['spectra']['source'].split(',')

				for j in sources:
					keys = ref_list[str(names[i])]['sources'][int(j)-1].keys()

					if 'bibcode' in keys:
						string = ref_list[str(names[i])]['sources'][int(j)-1]['reference']
						string = string.replace("(","").replace(")","")
						print(string)
						ref = {'name':string, 
								'url':'https://ui.adsabs.harvard.edu/abs/'+str(ref_list[str(names[i])]['sources'][int(j)-1]['bibcode'])+'/abstract'} #ADS link from bibcode

						list_of_sources.append(ref)
					elif 'url' in keys:
						ref = {'name':ref_list[str(names[i])]['sources'][int(j)-1]['name'], 
								'url':ref_list[str(names[i])]['sources'][int(j)-1]['url']}
						list_of_sources.append(ref)
				data[names[i]]['spectra']['source'] = list_of_sources

				#Save the data
				file = open('./SNE-OpenSN-Data/spectraJSON/'+str(names[i])+'/'+str(names[i])+'_'+str(n)+'.json', 'w')
				json.dump(data, file)

				n+=1