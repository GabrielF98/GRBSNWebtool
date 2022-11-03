'''
This is going to be a file that I can run to tell me all the tags that have been used in the master files for the webtool.
'''

import pandas as pd
import glob, os
from os.path import exists # Check if a file exists

# List of GRB-SNe that I have text file data on so far.
root = os.getcwd()
dirs = [ item for item in os.listdir(root) if os.path.isdir(os.path.join(root, item)) ]

trial_list = []
for i in dirs:
    if 'GRB' in str(i) or 'SN' in str(i):
        trial_list.append(i)

# Go through the list of folders and check if there's a readme. 
# If there is a readme, check for master files. If there are any then add the tags from those files to the master lists for radio, optical and xray. 
xray_keywords = []
radio_keywords = []
optical_keywords = []
spectra_keywords = []

for i in range(len(trial_list)):
	print(trial_list[i])
	if exists(trial_list[i]+'/'+trial_list[i]+'_Optical_Master.txt'):
		op_master = pd.read_csv(trial_list[i]+'/'+trial_list[i]+'_Optical_Master.txt', header=0, sep='\t', index_col=None)
		optical_keywords = optical_keywords+list(op_master.keys())

	if exists(trial_list[i]+'/'+trial_list[i]+'_Radio_Master.txt'):
		rad_master = pd.read_csv(trial_list[i]+'/'+trial_list[i]+'_Radio_Master.txt', header=0, sep='\t')
		radio_keywords = radio_keywords+list(rad_master.keys())

	if exists(trial_list[i]+'/'+trial_list[i]+'_Spectra_Master.txt'):
		spec_master = pd.read_csv(trial_list[i]+'/'+trial_list[i]+'_Spectra_Master.txt', header=0, sep='\t')
		spectra_keywords = spectra_keywords+list(spec_master.keys())

	if exists(trial_list[i]+'/'+trial_list[i]+'_Xray_Master.txt'):
		x_master = pd.read_csv(trial_list[i]+'/'+trial_list[i]+'_Xray_Master.txt', header=0, sep='\t')
		xray_keywords = xray_keywords+list(x_master.keys())

xray = list(set(xray_keywords))
radio = list(set(radio_keywords))
optical = list(set(optical_keywords))
spectra = list(set(spectra_keywords))

# Prints
print('The xray master files use these keywords: \n')
print(xray)
print(len(xray))
print('The optical master files use these keywords: \n')
print(optical)
print(len(optical))
print('The radio master files use these keywords: \n')
print(radio)
print(len(radio))
print('The spectra master files use these keywords: \n')
print(spectra)
print(len(spectra))