import numpy as np
import pandas as pd

#The requests module
import requests
import json

#Add the bit for the database access:
import sqlite3
def get_db_connection():
	conn = sqlite3.connect('Masterbase.db')
	conn.row_factory = sqlite3.Row
	return conn


#Return ADS urls of the primary sources
def bibcode_names():
	conn = get_db_connection()
	urls = conn.execute('SELECT DISTINCT(PrimarySources) FROM SQLDataGRBSNe')
	bibcodes = []
	hyperlinks = [] 
	for i in urls:
		
		if str(i[0])[0:10] == 'https://ui':

			#Split the bibcode into a list by breaking it each time a / appears
			bibcodes.append(str(i[0]).split('/')[4].replace('%26', '&'))
			hyperlinks.append(str(i[0]))
		#Skip anything without https://ui
		else:
			continue
	conn.close()
	
	return bibcodes, hyperlinks

bibcodes, hyperlinks = bibcode_names()

#API Access
#Code copied from the howto for the ADS API (though some of it is mine too)
#https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb

#Send query to ADS and get data back
token = 'vs2uU32JWGtrTQwOFtumfDmmDlCFe2QSJ3rwSOvv'

dictionary = {}
for i in range(len(bibcodes)):

	bibcode = {"bibcode":[str(bibcodes[i])], "format": "%m %Y"}
	r = requests.post("https://api.adsabs.harvard.edu/v1/export/custom", \
	                 headers={"Authorization": "Bearer " + token, "Content-type": "application/json"}, \
	                 data=json.dumps(bibcode))
	print(r.json())

	#dictionary[str(hyperlinks[i])] = r.json()['export']
	author_list = r.json()['export']
	author_split = r.json()['export'].split(',')

	dictionary_a={}
	if len(author_split)>2:
		dictionary_a['names'] = author_split[0]+' et al.'
		dictionary_a['year'] = author_list[-5:-1]
	else:
		dictionary_a['names'] = author_list[:-6]
		dictionary_a['year'] = author_list[-5:-1]
	dictionary[str(hyperlinks[i])] = dictionary_a

#Save the dictionary with json.dump()
file = open("citations.json", 'w')
json.dump(dictionary, file, sort_keys=True, indent=4, separators=(',', ': '))
file.close()

#Return ADS urls of the secondary sources
def secondary_bibcode_names():
	conn = get_db_connection()
	urls = conn.execute('SELECT DISTINCT(SecondarySources) FROM SQLDataGRBSNe')
	bibcodes = []
	hyperlinks = [] 
	for i in urls:
		
		if str(i[0])[0:10] == 'https://ui':

			#Split the bibcode into a list by breaking it each time a / appears
			bibcodes.append(str(i[0]).split('/')[4].replace('%26', '&'))
			hyperlinks.append(str(i[0]))
		#Skip anything without https://ui
		else:
			continue
	conn.close()
	
	return bibcodes, hyperlinks

bibcodes2, hyperlinks2 = secondary_bibcode_names()

#API Access
#Code copied from the howto for the ADS API (though some of it is mine too)
#https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb

dictionary2 = {}
for i in range(len(bibcodes2)):

	bibcode2 = {"bibcode":[str(bibcodes2[i])], "format": "%m %Y"}
	r = requests.post("https://api.adsabs.harvard.edu/v1/export/custom", \
	                 headers={"Authorization": "Bearer " + token, "Content-type": "application/json"}, \
	                 data=json.dumps(bibcode2))
	print(r.json())
	# dictionary2[str(hyperlinks2[i])] = r.json()['export']

	author_list = r.json()['export']
	author_split = r.json()['export'].split(',')

	dictionary_a={}
	if len(author_split)>2:
		dictionary_a['names'] = author_split[0]+' et al.'
		dictionary_a['year'] = author_list[-5:-1]
	else:
		dictionary_a['names'] = author_list[:-6]
		dictionary_a['year'] = author_list[-5:-1]
	dictionary2[str(hyperlinks2[i])] = dictionary_a
#Save the dictionary with json.dump()
file = open("citations2.json", 'w')
json.dump(dictionary2, file, sort_keys=True, indent=4, separators=(',', ': '))
file.close()



