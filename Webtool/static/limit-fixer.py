'''
This file will fix me having messed up the upper limits in optical
'''

import glob
import os
import numpy as np
import pandas as pd
from plotfuncs import list_grbs_with_data as events_lister

event_list = events_lister()
# Possible optical data tags in filenames.
optical_filetags = ['optical', 'nir', 'uv', 'ir']

# Run through all the files. Convert them to the format we want.
for i in range(len(event_list)):

	os.chdir("SourceData/")
	os.chdir(event_list[i])
	
	file_list = glob.glob("*.txt")

	# Check if the readme exists already. If it does then the files are ready to parse.
	if 'readme.txt' in file_list:
		for file in file_list:
			# Optical files
			if any(substring in file.lower() for substring in optical_filetags):
				data = pd.read_csv(file, sep='\t')

				new_mag_limit = np.zeros(len(data['mag_limit']), dtype=int)

				for i in range(len(data['mag_limit'])):
					new_mag_limit[i] = int(data['mag_limit'][i]*(-1))
				
				data['mag_limit'] = new_mag_limit

				data.to_csv(file, sep='\t', index=False, na_rep='NaN')
	
	os.chdir('..')
	os.chdir('..')