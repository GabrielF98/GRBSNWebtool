''' 
Creates a markdown readme from the txt readmes for the GRB-SN data files. 
'''

import snakemd
import os

# List of the folders to look for.
folders = []
for file in os.listdir():
    if os.path.isdir(file):
        if 'GRB' in file:
        	folders.append(file)
        elif 'SN' in file:
        	folders.append(file)

folders = ['GRB030329-SN2003dh']
# Loop over the folders.
for folder in folders:

	# Open the existing text readme. 
	with open(folder+'/readme.txt', 'r') as readme:
		readmelines = readme.readlines()

	# Create a markdown doc in the correct folder. 
	doc = snakemd.new_doc(folder+'/readme.md')

	# 