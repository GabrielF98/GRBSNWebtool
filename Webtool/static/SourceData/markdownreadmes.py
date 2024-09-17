'''
Creates readme.md from the readme.txt for the GRB-SN data files.
'''

import argparse
import os

from snakemd import new_doc

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--grbsn', type=str, required=False)
    args = parser.parse_args()

    if args.grbsn:
        folders = [args.grbsn]

    else:
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
            with open(folder+'/readme.txt', 'r', encoding='utf-8') as readme:
                readmelines = readme.readlines()

            if 'Filename:'==readmelines[2]:
                continue


            # Locate the limes in the file where the breaks between the files are.
            linenos = []
            for j, line in enumerate(readmelines):
                if '=========================================================\n' == line:
                    linenos.append(j)

            # Create a markdown doc in the correct folder.
            doc = new_doc()

            # The first line has the GRB-SN ID.
            doc.add_heading(readmelines[0].split(' ')[2])

            doc.add_paragraph("The text files listed below were downloaded from papers on\
                [NASA/ADS](https://ui.adsabs.harvard.edu) and converted to the GRBSN\
                [format](https://github.com/GabrielF98/GRBSNWebtool/tree/master/Webtool/static/SourceData).\
            The 'Master.txt' file(s) are a combination of these text files and contain all\
            of the downloaded data for a paticular wavelength range.")

            # Loop over the readme between the ========= marks that divide the files.
            for i in range(len(linenos)):
                # The filename
                doc.add_heading((readmelines[linenos[i]+1]).split(' ')[1], 3)
                p = doc.add_paragraph('**'+readmelines[linenos[i]+2].split(' ')[0]+'** ' +
                                    readmelines[linenos[i]+2].split(' ')[1])
                p.add_paragraphinsert_link = (readmelines[linenos[i]+2].split(' ')[1],
                                            readmelines[linenos[i]+2].split(' ')[1])  # The source
                doc.add_paragraph('**'+(readmelines[linenos[i]+3]).split(':')[0]+':** ' +
                                (readmelines[linenos[i]+3]).split(':')[1])  # The datatype

                # Add a new line for each note.
                doc.add_paragraph('**Notes:**')
                # Is it the last file
                # No
                if i+1 != len(linenos):
                    # Range from the first note to the last.
                    for note in range(linenos[i+1]-(linenos[i]+5)):
                        doc.add_paragraph(readmelines[linenos[i]+5+note])  # Notes
                # Yes
                else:  # If its the last file keep going until the end of the notes.
                    k = len(readmelines)-(linenos[i])
                    if k == 1:  # Range (0) is [0, 1]
                        doc.add_paragraph(readmelines[linenos[i]+5+note])  # Notes

                    else:
                        # Range from the first note to the last.
                        for note in range(len(readmelines)-(linenos[i]+5)):
                            doc.add_paragraph(
                                readmelines[linenos[i]+5+note])  # Notes

            # Create the doc.
            doc.dump(folder+"/readme")
