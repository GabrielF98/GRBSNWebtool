'''
Converts any Swift xrtlc files to the correct format to be plotted by the tool.
'''

import os

import numpy as np

PATH_TO_SOURCE_DATA = "../static/SourceData/"
dirs = [
    item
    for item in os.listdir(PATH_TO_SOURCE_DATA)
    if os.path.isdir(os.path.join(PATH_TO_SOURCE_DATA, item))
]

eventlist = []
for i in dirs:
    if 'GRB' in str(i) or 'SN' in str(i):
        eventlist.append(os.path.join(PATH_TO_SOURCE_DATA, i))

# Loop over all folders
for folder in eventlist:
    # Check if that folder has an xrtlc
    if os.path.exists(
        os.path.join(
            folder, os.path.basename(folder).split("-")[0] + "xrtlc.txt"
        )
    ):
        print(folder)
        # Read and write to the file
        with open(
            os.path.join(
                folder, os.path.basename(folder).split("-")[0] + "xrtlc.txt"
            ),
            "r",
        ) as fnew:
            # Open and read lines of the file
            f = fnew.readlines()
            f = np.array(f)

        # Check if we already fixed this file
        if f[0]=='col1\tcol2\tcol3\tcol4\tcol5\tcol6\tcol7\n':
            print("already fixed")
        else:
            with open(
                os.path.join(
                    folder,
                    os.path.basename(folder).split("-")[0] + "xrtlc.txt",
                ),
                "w",
                encoding="utf-8",
            ) as fnew:

                # Skip the big header line
                start = 0
                for i in range(len(f)):
                    if 'READ' in str(f[i]):
                        start = i+1
                        print('start is:', start)

                # Write a header line
                fnew.write('col1\tcol2\tcol3\tcol4\tcol5\tcol6\tcol7\n')

                # Loop through the lines to find what we need:
                code = 0

                for i in range(start, len(f)):
                    # make sure its not a 'NO NO NO NO NO' line etc
                    if 'Flux' not in str(f[i]) and 'NO' not in str(f[i]):
                        if 'WTSLEW' in str(f[i]):
                            code = 1
                            if 'upper limits' in str(f[i]):
                                code = 2
                            elif 'lower limits' in str(f[i]):
                                code = 3

                        elif 'WT' in str(f[i]):
                            code = 4
                            if 'upper limits' in str(f[i]):
                                code = 5
                            elif 'lower limits' in str(f[i]):
                                code = 6

                        elif 'PC' in str(f[i]):
                            code = 7
                            if 'upper limits' in str(f[i]):
                                code = 8
                            elif 'lower limits' in str(f[i]):
                                code = 9
                        else:
                            code = code
                            to_write = str(f[i]).replace('\n', '')+'\t'+str(code)+'\n'
                            fnew.writelines(to_write)
