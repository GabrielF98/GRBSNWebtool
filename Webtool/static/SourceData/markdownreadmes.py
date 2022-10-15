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

# Loop over the folders.
for folder in folders:

	# Check if the readme.txt file exists yet.
	if 'readme.txt' in os.listdir(folder):
		# Open the existing text readme. 
		with open(folder+'/readme.txt', 'r') as readme:
			readmelines = readme.readlines()


		# Locate the limes in the file where the breaks between the files are. 
		linenos = []
		for j, line in enumerate(readmelines):
			if '=========================================================\n' == line:
				linenos.append(j)

		# Create a markdown doc in the correct folder. 
		doc = Document(folder+"/readme")
		doc.add_header(readmelines[0].split(' ')[2]) # The first line has the GRB-SN ID. 

		doc.add_paragraph("The text files listed below were downloaded from papers on [NASA/ADS](https://ui.adsabs.harvard.edu) and converted to the GRBSN [format](https://github.com/GabrielF98/GRBSNWebtool/tree/master/Webtool/static/SourceData). The 'Master.txt' file(s) are a combination of these text files and contain all of the downloaded data for a paticular wavelength range.") # Next line explains the master files. 

		# Loop over the readme between the ========= marks that divide the files. 
		for i in range(len(linenos)):
			doc.add_header((readmelines[linenos[i]+1]).split(' ')[1], 3) # The filename
			p = doc.add_paragraph('**'+readmelines[linenos[i]+2].split(' ')[0]+'** '+readmelines[linenos[i]+2].split(' ')[1])
			p.add_paragraphinsert_link = (readmelines[linenos[i]+2].split(' ')[1], readmelines[linenos[i]+2].split(' ')[1]) # The source
			doc.add_paragraph('**'+(readmelines[linenos[i]+3]).split(':')[0]+':** '+(readmelines[linenos[i]+3]).split(':')[1]) # The datatype
			
			# Add a new line for each note.
			doc.add_paragraph('**Notes:**')
			# Is it the last file
			# No
			if i+1!=len(linenos):
				for note in range(linenos[i+1]-(linenos[i]+5)): # Range from the first note to the last.
					doc.add_paragraph(readmelines[linenos[i]+5+note]) # Notes
			# Yes
			else: # If its the last file keep going until the end of the notes.
				k = len(readmelines)-(linenos[i])
				if k==1: # Range (0) is [0, 1]
					doc.add_paragraph(readmelines[linenos[i]+5+note]) # Notes

				else: 
					for note in range(len(readmelines)-(linenos[i]+5)): # Range from the first note to the last.
						doc.add_paragraph(readmelines[linenos[i]+5+note]) # Notes
		
		# Create the doc. 
		doc.output_page()