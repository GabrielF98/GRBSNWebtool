#Add the bit for the database access:
import sqlite3
import pandas as pd
import numpy as np
#The requests module
import requests
import json
def get_db_connection():
    conn = sqlite3.connect('Webtool/static/Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Connect to db
conn = get_db_connection()

#Ok new plan
#Going to give it a go with the UNION and INTERSECT commands
query = (f"SELECT GRB, SNe, GROUP_CONCAT(e_iso), GROUP_CONCAT(E_p), GROUP_CONCAT(z), GROUP_CONCAT(T90), GROUP_CONCAT(e_k), GROUP_CONCAT(ni_m), GROUP_CONCAT(ej_m), GROUP_CONCAT(PrimarySources), GROUP_CONCAT(SecondarySources) FROM SQLDataGRBSNe GROUP BY GRB, SNe ORDER BY GRB, SNe;")
df = pd.read_sql(query, conn)

df = df.rename({'GROUP_CONCAT(e_iso)':'E$_{\\gamma, iso}$ [ergs]', 'GROUP_CONCAT(E_p)':'E$_p$ [keV]', 'GROUP_CONCAT(z)':'z', 'GROUP_CONCAT(T90)':'T$_{90}}$ [sec]', 'GROUP_CONCAT(e_k)':'E$_k$ [erg]', 'GROUP_CONCAT(ni_m)':'M$_{Ni}$ [M$_\\odot$]', 'GROUP_CONCAT(ej_m)':'M$_{Ej}$ [M$_\\odot$]', 'GROUP_CONCAT(PrimarySources)':'Primary', 'GROUP_CONCAT(SecondarySources)':'Secondary'}, axis=1)


#Convert the column for the GRB names to string format so we dont lose any leading zeros
df['GRB'] = df['GRB'].astype('str')


event_type = []
for i in range(len(df['GRB'])):
    if df['GRB'][i] == None:
        event_type.append('Orphan Afterglow')
    elif df['SNe'][i] == None:
        event_type.append('Photometric SN')
    else:
        event_type.append('Spectroscopic SN')

df['Event Type'] = event_type

# #Convert the E_iso and E_k to 10^52 scale
# for i in range(len(df['GRB'])):
#     if df['E$_{\\gamma, iso}$ [ergs]'][i]!=None:
#             new_vals = []
#             for j in list(df['E$_{\\gamma, iso}$ [ergs]'][i].split(',')):
#                 if '>' or '<' not in str(j):
#                     new_vals.append(j[0]+str(float(j[1:])/1e52))
#                 else:
#                     new_vals.append(np.float(j)/1e52)

#             df['E$_{\\gamma, iso}$ [ergs]'][i] = str(new_vals)

#     if df['E$_k$ [erg]'][i]!=None:
#             new_vals = []
#             for j in list(df['E$_k$ [erg]'][i].split(',')):
#                 if '>' or '<' not in str(j):
#                     new_vals.append(j[0]+str(float(j[1:])/1e52))
#                 else:
#                     new_vals.append(np.float(j)/1e52)

#             df['E$_k$ [erg]'][i] = str(new_vals)

#Return ADS urls of the primary sources
#Send query to ADS and get data back
token = 'vs2uU32JWGtrTQwOFtumfDmmDlCFe2QSJ3rwSOvv'
def bibcode_names(adsurl):
    if str(adsurl)[0:10] == 'https://ui':

        #Split the bibcode into a list by breaking it each time a / appears
        bibcode = str(adsurl).split('/')[4].replace('%26', '&')
    else:
        bibcode = 'No bibcode'

    return bibcode


#Return
bibnames = []
citelist = []

citerefs = []
for i in range(len(df['GRB'])):
    sub_citerefs = []
    if df['Primary'][i]!=None:

        for j in list(df['Primary'][i].split(',')):
            bibcode = bibcode_names(j)
            if bibcode!='No bibcode':
                bibcode2 = {"bibcode":[str(bibcode)], "format": "%m %Y"}
                r = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex", \
                                 headers={"Authorization": "Bearer " + token, "Content-type": "application/json"}, \
                                 data=json.dumps(bibcode2))
                #Get the ones that are unique
                if bibcode in bibnames:
                    print('already there')
                else:
                    bibnames.append(bibcode)
                    citelist.append(str(r.json()['export']))

                #The reference for the table
                sub_citerefs.append("\\cite{"+bibcode+"}")
    if df['Secondary'][i]!=None:

        for j in list(df['Secondary'][i].split(',')):
            bibcode = bibcode_names(j)
            if bibcode!='No bibcode':
                bibcode2 = {"bibcode":[str(bibcode)], "format": "%m %Y"}
                r = requests.post("https://api.adsabs.harvard.edu/v1/export/bibtex", \
                                 headers={"Authorization": "Bearer " + token, "Content-type": "application/json"}, \
                                 data=json.dumps(bibcode2))
                #Get the ones that are unique
                if bibcode in bibnames:
                    print('already there')
                else:
                    print(bibcode)
                    bibnames.append(bibcode)
                    citelist.append(str(r.json()['export']))

                #The reference for the table
                sub_citerefs.append("\\cite{"+bibcode+"}")
    citerefs.append(sub_citerefs)
df['Refs.'] = citerefs
#Write the list of citations to a txt for use in latex
textfile = open("cites.txt", "w")
for element in citelist:
    textfile.write(element + "\n")
textfile.close()

df.to_csv('table4paper.csv', index=False)














