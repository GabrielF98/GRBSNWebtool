import numpy as np

# open text file
file = 'GoodXRTData/GRB171205Axrtlc.txt'
f = open(file, 'r')
f = f.readlines()
f = np.array(f)

# Loop through the lines to find what we need:
read_terr = -1
wt_slew = -1
wt = -2
wt_limit = -3
pc = -4
pc_limit = -5

# List that will store the index the rows change datatype at
indices = []

for i in range(len(f)):

    # Check what line has READ TERR 1 2
    print(f[i])
#     if 'WTSLEW' in str(f[i]]):
        

# with open('test.txt', 'w') as newf:
