'''
This script needs to be run to return the citation information from NASA ADS.
This is the data that eventually appears in the table on the event page.
'''

import json
import sqlite3
import requests
import pandas as pd

def get_db_connection():
    """
    Connect to the master database.
    """
    conn = sqlite3.connect('Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

def bibcode_names(type):
    """
    Return ADS urls of the primary sources
    """
    conn = get_db_connection()
    urls1 = conn.execute(f'SELECT DISTINCT({type}) FROM SQLDataGRBSNe')
    urls2 = conn.execute('SELECT DISTINCT(source) FROM TrigCoords')
    urls3 = conn.execute('SELECT DISTINCT(source) FROM PeakTimesMags')
    urls = []

    for i in urls1:
        if i not in urls:
            urls.append(i)

    # We don't want to get the sources from TrigCoords and PeakTimesMags
    # if we are using this funcition for secondary sources.
    if type == 'PrimarySources':
        for i in urls2:
            if i not in urls:
                urls.append(i)

        for i in urls3:
            if i not in urls:
                urls.append(i)

    bibcodes = []
    hyperlinks = []
    randoms = []
    for i in urls:

        if str(i[0])[0:10] == 'https://ui':

            #Split the bibcode into a list by breaking it each time a / appears
            bibcodes.append(str(i[0]).split('/')[4].replace('%26', '&'))
            hyperlinks.append(str(i[0]))
        #Include anything without https://ui but dont go to ADS
        else:
            randoms.append(i[0])
    conn.close()

    return bibcodes, hyperlinks, randoms

# Get bibcodes.
bibcodes, hyperlinks, randoms = bibcode_names('PrimarySources')
bibcodes2, hyperlinks2, randoms2 = bibcode_names('SecondarySources')

#API Access
#Code copied from the howto for the ADS API (though some of it is mine too)
#https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb

#Send query to ADS and get data back
token = 'vs2uU32JWGtrTQwOFtumfDmmDlCFe2QSJ3rwSOvv'

dictionary = {}
for i in range(len(bibcodes)):

    bibcode = {"bibcode":[str(bibcodes[i])], "format": "%m %Y"}
    r = requests.post("https://api.adsabs.harvard.edu/v1/export/custom", \
                     headers={"Authorization": "Bearer " + token, \
                     "Content-type": "application/json"}, \
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

#Take care of the randoms
for i in range(len(randoms)):
    dictionary[randoms[i]] = randoms[i]

#Save the dictionary with json.dump()
with open("citations/citations.json", 'w', encoding='utf-8') as file:
    json.dump(dictionary, file, indent=4, separators=(',', ': '))

#API Access
#Code copied from the howto for the ADS API (though some of it is mine too)
#https://github.com/adsabs/adsabs-dev-api/blob/master/Converting_curl_to_python.ipynb

dictionary2 = {}
for i in range(len(bibcodes2)):

    bibcode2 = {"bibcode":[str(bibcodes2[i])], "format": "%m %Y"}
    r = requests.post("https://api.adsabs.harvard.edu/v1/export/custom", \
         headers={"Authorization": "Bearer " + token, \
         "Content-type": "application/json"}, \
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

#Take care of the randoms
for i in range(len(randoms2)):
    dictionary2[randoms2[i]] = randoms2[i]
#Save the dictionary with json.dump()
with open("citations/citations2.json", 'w', encoding='utf-8') as file:
    json.dump(dictionary2, file, indent=4, separators=(',', ': '))


def grb_names():
    """
    # Get the names of all GRB-SNe in the webtool.
    """
    conn = get_db_connection()
    names = conn.execute('SELECT DISTINCT GRB, SNe FROM SQLDataGRBSNe')
    grbs = []
    for i in names:
        if str(i[0]) != 'None' and str(i[1]) != 'None':
            if 'AT' in str(i[1]):
                grbs.append('GRB'+str(i[0])+'-'+str(i[1]))
            else:
                grbs.append('GRB'+str(i[0])+'-SN'+str(i[1]))

        elif str(i[1])=='None':
            grbs.append('GRB'+str(i[0]))

        elif str(i[0]) == 'None':
            if 'AT' in str(i[1]):
                grbs.append(str(i[1]))
            else:
                grbs.append('SN'+str(i[1]))
    conn.close()

    return grbs

# Go to all the GRB-SN source files and get the names.
folder_names = grb_names()

# Get the bibcodes and hyperlinks
bibcodes = []
hyperlinks = []
randoms = []
for folder in folder_names:
    df = pd.read_csv('SourceData/'+str(folder)+'/'+str(folder)+'filesources.csv')
    citations = df['Reference']

    for i in citations:
        if str(i)[0:10] == 'https://ui':

            #Split the bibcode into a list by breaking it each time a / appears
            bibcodes.append(str(i).split('/')[4].replace('%26', '&'))
            hyperlinks.append(str(i))
        
        elif 'tns' in str(i):
            randoms.append(str(i))


dictionary3 = {}
for i in range(len(bibcodes)):

    bibcode = {"bibcode":[str(bibcodes[i])], "format": "%m %Y"}
    r = requests.post("https://api.adsabs.harvard.edu/v1/export/custom", \
                     headers={"Authorization": "Bearer " + token, \
                     "Content-type": "application/json"}, \
                     data=json.dumps(bibcode))
    print(r.json())

    author_list = r.json()['export']
    author_split = r.json()['export'].split(',')

    dictionary_a={}
    if len(author_split)>2:
        dictionary_a['names'] = author_split[0]+' et al.'
        dictionary_a['year'] = author_list[-5:-1]
    else:
        dictionary_a['names'] = author_list[:-6]
        dictionary_a['year'] = author_list[-5:-1]
    dictionary3[str(hyperlinks[i])] = dictionary_a

# Deal with the randoms
for i in range(len(randoms)):
    dictionary3[randoms[i]] = {'names':'Transient Name Server', 'year':''}

#Save the dictionary with json.dump()
with open("citations/citations(ADSdatadownloads).json", 'w', encoding='utf-8') as file:
	json.dump(dictionary3, file, indent=4, separators=(',', ': '))
