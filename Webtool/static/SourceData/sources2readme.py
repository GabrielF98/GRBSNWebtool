'''
This script will let the data from the filesources csv be added to the readme.
'''

import os
import pandas as pd

# List of the folders to look for.
folders = []
for file in os.listdir():
    if os.path.isdir(file):
        if 'GRB' in file:
            folders.append(file)
        elif 'SN' in file:
            folders.append(file)


for folder in folders:
    # Open the filesources file.
    filesources = pd.read_csv(folder+'/'+folder+'filesources.csv', header=0)

    # Check if the readme.txt file exists yet.
    if 'readme.txt' in os.listdir(folder):

        # Open the readme file.
        with open(folder+'/readme.txt', 'r', encoding='utf-8') as readme:
            readme_lines = readme.readlines()

        # Loop over the readme filenames until they match a line
        index = [] # Record the line number where we need to insert the line
        datatypes = [] # Is the data optical, early etc.
        source = [] # Where is the data from.


        for i in range(len(readme_lines)):
            # Read the line and check have we written to this file's line before.
            if 'Filename:' in readme_lines[i] and 'Source:' not in readme_lines[i+1]:
                index.append(i+1) # Record line number where we want to insert this line.
                # Get the index in the df where that Filename occurs.
                new = filesources.loc[filesources['Filename']==readme_lines[i].split(":")[1][1:-1]]
                new = new.reset_index() # Reset the index

                # Save the data we want.
                datatypes.append(new['Status'])
                source.append(new['Reference'])


        # Write the new rows and the existing ones to the file.
        # For the datatypes
        for i in range(len(index)):
            print(len(datatypes[i]))
            print(datatypes[i][0])
            print(source[i][0])
            readme_lines.insert(index[i]+i*2, 'Data-type: '+datatypes[i][0]+'\n')
            readme_lines.insert(index[i]+i*2, 'Source: '+source[i][0]+'\n')

        # Write to the file
        with open(folder+'/readme.txt', 'w', encoding='utf-8') as file:
            readme_lines = "".join(readme_lines)
            file.write(readme_lines)
