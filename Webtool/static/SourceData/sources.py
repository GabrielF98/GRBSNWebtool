import pandas as pd
import numpy as np
import os
import glob

root = os.getcwd()
dirs = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

file_list = []
for i in dirs:
	if 'GRB' in str(i) or 'SN' in str(i):
		file_list.append(i)

# Go into the notion export and find the source list for the GRB or SN
loc = '/NotionExportMay22/'
root = root+loc
dirs2 = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

for i in dirs2:	
	print(i)
	if 'Download' in str(i):
		sourcefolder1 = str(i)+'/'

root = root+sourcefolder1
dirs3 = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

for i in dirs3:	
	print(i)
	if 'Source List' in str(i):
		sourcefolder2 = str(i)+'/'

root = root+sourcefolder2
dirs4 = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

# loop over the GRB-SN name list
for j in file_list:
	for i in dirs4:	
		if str(j) in str(i):
			print("I work")
			#List the csvs in this folder (i)
			csv_files = glob.glob(os.path.join(root+i, "*.csv"))
			
			#Read in the first csv (for some reason there are doubles of everything)
			df = pd.read_csv(csv_files[0])

			#Add a column saying what GRB-SN this is
			length = len(df)
			name_col = [j]*length

			df['GRB-SN'] = name_col

			#Write to a csv for these GRBs
			df.to_csv('./'+str(j)+'/'+str(j)+'filesources.csv', sep=',', index=False)







