import numpy as np

# open text file
file = r'GRB171205A/GRB171205Axrtlc.txt'


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

with open
for i in range(len(f)):
    print(f[i])
    if 'WTSLEW' in str(f[i]]):

    else:

        

# with open('test.txt', 'w') as newf:
