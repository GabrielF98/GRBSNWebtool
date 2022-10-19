import numpy as np
import pandas as pd

data = pd.read_csv('GRB031203-SN2003lw_Optical2.txt', header=0, sep='\t')

# Get positions where a certain value is reached. 
indices = np.where(data['mag'].isin([20.37, 20.14, 19.18, 18.13, 17.36, 16.38]))
dmag_vals = [0.05, 0.03, 0.03, 0.34, 0.42, 0.36]
mag_vals = [20.37, 20.14, 19.18, 18.13, 17.36, 16.38]
for k in range(len(indices[0])):
	for i in range(len(data['mag'])):
		if k<5:
			if indices[0][k]<i<indices[0][k+1]:
				data['mag'][i]+=mag_vals[k]
				# data['dmag'][i]+=data['dmag'][i]+dmag_vals[k]
		elif k==5:
			if i<38 and i>indices[0][k]:
				data['mag'][i]+=mag_vals[k]
				# data['dmag'][i]+=data['dmag'][i]+dmag_vals[k]

print(data)
data.to_csv('GRB031203-SN2003lw_Optical2.txt', sep='\t')