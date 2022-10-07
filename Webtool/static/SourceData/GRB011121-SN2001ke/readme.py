'''
This script will let the data from the filesources csv be added to the readme.  
'''

# Import 
import pandas as pd

# Open the filesources file. 
filesources = pd.read_csv('GRB011121-SN2001kefilesources.csv', header=0)

# Open the readme file.
with open('readme.txt', 'r') as readme:
	readme_lines = readme.readlines()

# Loop over the readme filenames until they match a line
index = [] # Record the line number where we need to insert the line
datatypes = [] # Is the data optical, early etc.
source = [] # Where is the data from.

for i in range(len(readme_lines)):
	if 'Filename:' in readme_lines[i]:
		index.append(i) # Record line number where we want to insert this line.
		loc = filesources.loc[filesources['Filename']==readme_lines[i].split(":")[1][1:-1]] # Get the index in the df where that Filename occurs.

		# Save the data we want. 
		datatypes.append(loc['Status'])
		source.append(loc['Reference'])

# Write the new rows and the existing ones to the file.
# For the datatypes
for i in range(len(index)):
	readme_lines.insert(index[i], datatypes[i])
	readme_lines.insert(index[i], source[i])

# Write to the file
with open('readme.txt', 'w') as file:
	file.writelines(readme_lines) 
