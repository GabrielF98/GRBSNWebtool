import numpy as np
import os
eventlist = os.listdir()
forbidden_folders = ['.DS_Store', 'GoodXRTData', '.ipynb_checkpoints']
for item in eventlist:
    if os.path.isdir(item):
        if str(item) in forbidden_folders:
            eventlist.remove(item)
    else:
        eventlist.remove(item)

# Loop over all folders
for folder in eventlist:
    if folder!='newfile.txt':
        #Check if that folder has an xrtlc
        filelist = os.listdir(folder)
        if str(folder).split('-')[0]+'xrtlc.txt' in filelist:
            #Read and write to the file
            with open(str(folder)+'/'+str(folder).split('-')[0]+'xrtlc.txt', 'r') as fnew: 
                #Open and read lines of the file
                f = fnew.readlines()
                f = np.array(f)

            with open(str(folder)+'/'+str(folder).split('-')[0]+'xrtlc.txt', 'w') as fnew:

                #Write a header line
                fnew.write('col1\tcol2\tcol3\tcol4\tcol5\tcol6\tcol7\n')

                # Loop through the lines to find what we need:
                code = 0

                for i in range(len(f)):
                    if 'WTSLEW' in str(f[i]):
                        code = 1
                    elif 'WT' in str(f[i]):
                        code = 2
                    elif 'WT' and 'limit' in str(f[i]):
                        code = 3
                    elif 'PC' in str(f[i]):
                        code = 4
                    elif 'PC' and 'limit' in str(f[i]):
                        code = 3
                    else:
                        code = code
                        to_write = str(f[i]).replace('\n', '')+' '+str(code)+'\n'
                        fnew.writelines(to_write)