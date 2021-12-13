#Shebang
#!/usr/bin/python3

#Imports
import numpy as np
import matplotlib.pyplot as plt

#The direct path to the database
path = "/Users/gabriel/Documents/GRB-SNe/Database/Webtool/"

#Add the bit for the database access:
import sqlite3
def get_db_connection():
    conn = sqlite3.connect(path+'Masterbase.db')
    conn.row_factory = sqlite3.Row
    return conn

#Data aquisition
def get():
    conn = get_db_connection()
    events = conn.execute('SELECT GRB, T90, e_iso FROM SQLDataGRBSNe')
    
    grbs = []
    t90 = []
    eiso = []
    for i in events:
    	grbs.append(i[0])
    	t90.append(i[1])
    	eiso.append(i[2])

    conn.close()

    return grbs, t90, eiso

#Return the data
grbs, t90, eiso = get()

eisob = []
grbsb = []

grbsc = []
t90b = []

#Convert the data to floats
for i in range(len(grbs)):
	#print(eiso[i])
	if str(eiso[i]) == 'None':
		continue
	else:
		#print(eiso[i])
		eisob.append(float(str(eiso[i])))
		grbsb.append((str(grbs[i])))

	#print(t90[i])
	if str(t90[i]) == 'None':
		print(str(t90[i]))
		continue

	#turn the > to just the number
	elif '>' or '<' or '~' in str(t90[i]):
		t90b.append(float(str(t90[i][1:])))
		grbsc.append((str(grbs[i])))

	else:
		#print(t90[i])
		t90b.append(float(str(t90[i])))
		grbsc.append((str(grbs[i])))

#Get the average if there are multiple values for the data
import pandas as pd
print(len(grbsc), len(t90b))
d1 = {'grbsc': grbsc, 't90': t90}
d2 = {'grbsb':grbsb, 'eiso': eisob}

data1 = pd.DataFrame(d1)
data2 = pd.DataFrame(d2)

#eiso graph with the nones removed
#First make a new df that has all non nan eisos and their associated grb name
data2.dropna(subset = ["eiso"], inplace=True)

#Groupby the GRB name and take the mean, this makes sure theres no duplicates.
data2 = data2.groupby('grbsb').mean().reset_index()

#Histogram
plt.hist(np.log10(data2['eiso']))
plt.xlabel('E$_{iso}$ (ergs)')
plt.ylabel('Frequency')
plt.savefig('GRBSNeEiso.pdf')

