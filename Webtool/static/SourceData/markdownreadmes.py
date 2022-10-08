''' 
Creates readme.md from the readme.txt for the GRB-SN data files. 
'''

from snakemd import Document
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


	# Locate the limes in the file where the breaks between the files are. 
	linenos = []
	for i, line in enumerate(readmelines):
		if '=========================================================\n' == line:
			linenos.append(i)

	print(linenos)
	# Create a markdown doc in the correct folder. 
	doc = Document(folder+"/readme")
	doc.add_header(readmelines[0]) # The first line has the GRB-SN ID. 

	# Loop over the readme between the ========= marks that divide the files. 
	for i in range(len(linenos)):
		doc.add_header((readmelines[linenos[i]+1]).split(' ')[1], 3) # The filename
		p = doc.add_paragraph('\*\*'+readmelines[linenos[i]+2].split(' ')[0]+'\*\*'+readmelines[linenos[i]+2].split(' ')[1])
		p.add_paragraphinsert_link = (readmelines[linenos[i]+2].split(' ')[1], readmelines[linenos[i]+2].split(' ')[1]) # The source
		doc.add_paragraph(readmelines[linenos[i]+3]) # The datatype
		
		# Add a new line for each note.
		# for note in range(linenos[i+1]-linenos[i]+5): # Range from the first note to the last.
		# 	doc.add_paragraph(readmelines[linenos[i]+5+note]) # Notes
	doc.output_page()

	# 