import numpy as np

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
	for i in urls:
		
		if str(i[0])[0:10] == 'https://ui':

			#Split the bibcode into a list by breaking it each time a / appears
			bibcodes.append(str(i[0]).split('/')[4])

		#Skip anything without https://ui
		else:
			continue
	conn.close()
	
	return bibcodes

bibcodes = bibcode_names()

#API Access
#Code copied from the howto for the ADS API (though some of it is mine too)
#https://github.com/adsabs/adsabs-dev-api/blob/master/Search_API.ipynb

#Generate the query
from urllib.parse import urlencode, quote_plus
query_list = []
for i in range(len(bibcodes)):
	query = {"bibcode":str(bibcodes[i])}
	encoded_query = urlencode(query,quote_via=quote_plus)

	query_list.append(encoded_query)

print(query_list)

#Send query to ADS and get data back









