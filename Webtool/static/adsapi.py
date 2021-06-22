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
print(bibcodes)
#API Access
#Code copied from the howto for the ADS API (though some of it is mine too)
#https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb

#Send query to ADS and get data back
token = 'oLH7C9g5twATAq6yW1PDHIAtAxaXQzNcSj71Az67'

authors = []
years = []

for i in range(len(bibcodes)):

	bibcode = {"bibcode":[str(bibcodes[i])], "format": "%m %Y"}
	r = requests.post("https://api.adsabs.harvard.edu/v1/export/custom", \
	                 headers={"Authorization": "Bearer " + token, "Content-type": "application/json"}, \
	                 data=json.dumps(bibcode))
	print(r.json())

	authors.append(r.json()['export'][:-5])
	years.append(r.json()['export'][-5:])

#Save the ads_url, name and year in one txt file		
import csv
with open('citations.csv', 'w') as f:
	writer = csv.writer(f, delimiter='\t')
	writer.writerows(zip(hyperlinks, authors, years))



