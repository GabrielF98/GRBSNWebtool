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

forbidden_lines = ['!Time\tT_+ve\tT_-ve\tFlux\tFluxpos\tFluxneg', 'NO\tNO\tNO\tNO\tNO']
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

            #Check if we already fixed this file
            if f[0]=='col1\tcol2\tcol3\tcol4\tcol5\tcol6\tcol7\n':
                print("already fixed")
            else:
                with open(str(folder)+'/'+str(folder).split('-')[0]+'xrtlc.txt', 'w') as fnew:

                    #Skip the big header line
                    start = 0
                    for i in range(len(f)):
                        if 'READ' in str(f[i]):
                            start = i+1
                            print('start is:', start)

                    #Write a header line
                    fnew.write('col1\tcol2\tcol3\tcol4\tcol5\tcol6\tcol7\n')

                    # Loop through the lines to find what we need:
                    code = 0

                    for i in range(start, len(f)):
                        if 'Flux' not in str(f[i]) and 'NO' not in str(f[i]): #make sure its not a 'NO NO NO NO NO' line etc
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
                                to_write = str(f[i]).replace('\n', '')+' '+str(code)+'\n'
                                fnew.writelines(to_write)