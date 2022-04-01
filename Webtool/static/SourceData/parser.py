import numpy as np
import os
eventlist = os.listdir()
forbidden_folders = ['.DS_Store', 'GoodXRTData']
for item in eventlist:
    if os.path.isdir(item):
        if str(item) in forbidden_folders:
            eventlist.remove(item)
    else:
        eventlist.remove(item)
eventlist = ['GRB171205A-SN2017iuk']
# Loop over all folders
for folder in eventlist:
    with open('newfile.txt', 'w') as fnew: 
        grb_name = str(list(folder.split('-'))[0])
        print(grb_name)
        folder = str(folder)
        # open text file
        file = folder+'/'+grb_name+'xrtlc.txt'


        f = open(file, 'r')
        f = f.readlines()
        f = np.array(f)

        # Loop through the lines to find what we need:
        code = 0

        for i in range(len(f)):
            print(f[i])
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
                to_write = str(f[i])+' '+str(code)
                fnew.writelines(to_write)